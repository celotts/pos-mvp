from typing import Any

from langchain.agents import create_agent
from langchain_core.globals import set_debug
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from service.agent_tools import (
    get_product_kardex,
    get_purchases_summary,
    get_sales_summary,
)

set_debug(True)


class InventoryAnalystAgent:
    def __init__(self, model_name: str = "qwen2.5-coder"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.tools: list[Any] = [
            get_sales_summary,
            get_purchases_summary,
            get_product_kardex,
        ]

        self.system_prompt = (
            "Eres un analista de inventarios. "
            "DEBES invocar tus herramientas (get_sales_summary, get_purchases_summary, get_product_kardex) "
            "para consultar la base de datos antes de dar una respuesta."
        )

        # create_agent no acepta 'prompt' directamente como argumento
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
        )

    async def run(self, query: str) -> str:
        # Pasa el SystemMessage junto a la consulta del usuario
        result = await self.agent_executor.ainvoke(
            {
                "messages": [
                    SystemMessage(content=self.system_prompt),
                    ("user", query),
                ]
            }
        )

        messages = result.get("messages")
        if not messages:
            raise KeyError("messages")

        return str(messages[-1].content)


agent_service = InventoryAnalystAgent()
