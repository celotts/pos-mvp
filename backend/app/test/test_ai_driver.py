import pytest
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from service.ai.driver import _make_agent_tool, _tool_params


class _FakeModel(BaseChatModel):
    """Modelo que hace UNA llamada a la tool `probe` y luego responde."""

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        has_tool_calls = any(
            c for m in messages for c in getattr(m, "tool_calls", []) or []
        )
        if has_tool_calls:
            content = AIMessage(content="RESULTADO_FINAL")
        else:
            content = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "probe",
                        "args": {"label": "demo"},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            )
        return ChatResult(generations=[ChatGeneration(message=content)])

    @property
    def _llm_type(self) -> str:
        return "fake"


async def _probe(db=None, store_id=None, label: str = "") -> dict:
    """Tool plana que expone el db/contexto que recibe del driver."""
    return {"db_is_fake": db == "SESSION_DB", "label": label}


@pytest.mark.asyncio
async def test_driver_injects_db_context_into_tool():
    """El `db` del contexto debe llegar a la tool (regresión del runtime=None)."""
    params = _tool_params(_probe)
    wrapped = _make_agent_tool(
        name="probe",
        description="sondea el contexto",
        func=_probe,
        params=params,
    )
    agent = create_agent(model=_FakeModel(), tools=[wrapped])

    result = await agent.ainvoke(
        input={"messages": [("user", "prueba")]},
        context={"db": "SESSION_DB", "store_id": None},
    )
    assert result["messages"][-1].content == "RESULTADO_FINAL"


@pytest.mark.asyncio
async def test_driver_tool_receives_runtime_not_null():
    """El runtime inyectado no debe ser None y debe llevar el contexto."""
    seen = {}

    async def _capture(db=None, store_id=None):
        seen["db"] = db
        return {"ok": True}

    wrapped = _make_agent_tool(
        name="capture",
        description="captura db",
        func=_capture,
        params=_tool_params(_capture),
    )
    agent = create_agent(model=_FakeModelCapture(), tools=[wrapped])

    result = await agent.ainvoke(
        input={"messages": [("user", "x")]},
        context={"db": "CTX_DB", "store_id": "S1"},
    )
    assert result["messages"][-1].content == "DONE"
    assert seen["db"] == "CTX_DB"


class _FakeModelCapture(_FakeModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        has_tool_calls = any(
            c for m in messages for c in getattr(m, "tool_calls", []) or []
        )
        if has_tool_calls:
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content="DONE"))]
            )
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "capture",
                                "args": {},
                                "id": "call_1",
                                "type": "tool_call",
                            }
                        ],
                    )
                )
            ]
        )
