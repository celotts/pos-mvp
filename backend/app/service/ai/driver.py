"""Driver de agentes basado en LangGraph/LangChain.

Es el ÚNICO módulo que conoce el framework de agentes. Convierte las tools
planas de `service.ai.tools` en tools de langchain y ejecuta el agente.
"""

import inspect
from typing import Any

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from service.ai.ports import ToolDef
from utils.logger import logger


def _tool_params(func) -> list[tuple[str, Any, Any]]:
    """Extrae [(name, annotation, default)] de los parámetros expuestos al LLM.

    Excluye `db` y `store_id`, que son contexto de ejecución inyectado por el
    driver y nunca deben formar parte del contrato del LLM. `default` es
    `...` para parámetros obligatorios.
    """
    params = inspect.signature(func).parameters
    out: list[tuple[str, Any, Any]] = []
    for name, param in params.items():
        if name in ("db", "store_id"):
            continue
        annotation = (
            param.annotation
            if param.annotation is not inspect.Parameter.empty
            else Any
        )
        default = (
            param.default
            if param.default is not inspect.Parameter.empty
            else ...
        )
        out.append((name, annotation, default))
    return out


def _format_default(default: Any) -> str:
    """Serializa un valor por defecto a una expresión Python válida."""
    return repr(default)


def _make_agent_tool(*, name: str, description: str, func, params) -> Any:
    """Construye una tool de langchain a partir de una tool plana.

    Genera dinámicamente un wrapper `runtime(runtime: ToolRuntime, *campos)`.
    Es crítico NO pasar `args_schema` explícito a `@tool`: cuando el schema se
    deja inferido, langchain reconoce `ToolRuntime` como argumento inyectable y
    lo puebla desde el `runtime.context` del grafo. Si se fuerza `args_schema`,
    esa detección se omite y `runtime` llega `None` (`db` se perdería).
    """
    required = [p for p in params if p[2] is ...]
    optional = [p for p in params if p[2] is not ...]

    def _decl(p: tuple[str, Any, Any]) -> str:
        pname, annotation, default = p
        ann = _annot_str(annotation)
        if default is ...:
            return f"{pname}: {ann}"
        return f"{pname}: {ann} = {_format_default(default)}"

    signature_parts = [_decl(p) for p in required + optional]
    signature = ", ".join(signature_parts)
    kwargs_call = ", ".join(f"{p[0]}={p[0]}" for p in required + optional)

    src = (
        "async def wrapped(runtime: ToolRuntime = None, "
        f"{signature}):\n"
        "    context = (runtime.context if runtime else None) or {}\n"
        "    db = context.get('db')\n"
        "    if db is None:\n"
        "        raise RuntimeError("
        "'No se encontró la sesión de base de datos en el contexto del agente.')\n"
        f"    return await func(db=db, store_id=context.get('store_id'), {kwargs_call})\n"
    )

    namespace: dict[str, Any] = {
        "ToolRuntime": ToolRuntime,
        "func": func,
        "RuntimeError": RuntimeError,
    }
    exec(compile(src, f"<agent_tool:{name}>", "exec"), namespace)  # noqa: S102
    wrapped = namespace["wrapped"]
    wrapped.__name__ = name
    wrapped.__qualname__ = name

    return tool(
        name_or_callable=name,
        description=description,
    )(wrapped)


def _annot_str(annotation: Any) -> str:
    """Convierte una anotación de tipo a su cadena importable en el exec."""
    if annotation in (Any, inspect.Parameter.empty):
        return "Any"
    return annotation.__name__ if hasattr(annotation, "__name__") else str(annotation)


class LangGraphAgentDriver:
    """Implementa un driver de agentes con langchain.create_agent."""

    def __init__(self, chat_model: BaseChatModel):
        self.chat_model = chat_model
        self._executors: dict[tuple[str, tuple[str, ...]], Any] = {}

    def _wrap_tool(self, tool_def: ToolDef):
        description = tool_def.description or tool_def.name
        params = _tool_params(tool_def.func)
        return _make_agent_tool(
            name=tool_def.name,
            description=description,
            func=tool_def.func,
            params=params,
        )

    def _get_executor(self, system_prompt: str, tools: list[ToolDef]):
        key = (system_prompt, tuple(t.name for t in tools))
        if key not in self._executors:
            wrapped_tools = [self._wrap_tool(t) for t in tools]
            self._executors[key] = create_agent(
                model=self.chat_model,
                tools=wrapped_tools,
            )
        return self._executors[key]

    def _build_messages(self, system_prompt: str, query: str, store_id=None):
        messages: list[Any] = [SystemMessage(content=system_prompt)]
        if store_id:
            query = (
                f"[Contexto: estás analizando ÚNICAMENTE la tienda con id='{store_id}'. "
                f"Las herramientas ya reciben esta tienda automáticamente; "
                f"no ingreses identificadores en las llamadas.]\n{query}"
            )
        messages.append(("user", query))
        return messages

    async def run(
        self,
        *,
        system_prompt: str,
        query: str,
        tools: list[ToolDef],
        db,
        store_id=None,
    ) -> str:
        executor = self._get_executor(system_prompt, tools)
        try:
            result = await executor.ainvoke(
                input={"messages": self._build_messages(system_prompt, query, store_id)},
                context={"db": db, "store_id": store_id},
            )
            messages = result.get("messages")
            if not messages:
                raise KeyError("messages")
            return str(messages[-1].content)
        except Exception:  # noqa: BLE001  (degradación honesta del agente)
            logger.exception("Error ejecutando agente de IA")
            return (
                "Error: No se pudo generar el análisis en este momento. "
                "Verifica que el servicio de IA (Ollama) esté disponible."
            )


__all__ = ["LangGraphAgentDriver"]