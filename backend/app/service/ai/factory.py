"""Fábrica del AgentService. Cambiar de proveedor = 1 línea de config."""

from service.ai.agent_service import AgentService
from service.ai.driver import LangGraphAgentDriver
from service.ai.providers import chat_provider_factory, embedding_provider_factory


def build_agent_service() -> AgentService:
    """Construye el AgentService completo a partir de la configuración.

    Proveedor LLM: `settings.LLM_PROVIDER` (ollama por defecto, anthropic alternativo).
    Proveedor de embeddings: `settings.EMBEDDING_MODEL` vía Ollama.
    """
    chat_provider = chat_provider_factory()
    embedding_provider = embedding_provider_factory()
    driver = LangGraphAgentDriver(chat_model=chat_provider.get_chat_model())
    return AgentService(
        chat_provider=chat_provider,
        embedding_provider=embedding_provider,
        driver=driver,
    )


ai_service = build_agent_service()


__all__ = ["AgentService", "ai_service", "build_agent_service"]