"""Fábricas de proveedores de IA según `settings.LLM_PROVIDER`."""

from core.config import settings
from service.ai.providers.anthropic import AnthropicChatProvider
from service.ai.providers.ollama import OllamaChatProvider, OllamaEmbeddingProvider
from utils.logger import logger

SUPPORTED_CHAT_PROVIDERS = ("ollama", "anthropic")


def chat_provider_factory():
    """Construye el chat provider configurado (ollama por defecto)."""
    provider = (getattr(settings, "LLM_PROVIDER", None) or "ollama").strip().lower()
    if provider == "anthropic":
        logger.info("Usando chat provider: anthropic")
        return AnthropicChatProvider()
    if provider == "ollama":
        logger.info("Usando chat provider: ollama")
        return OllamaChatProvider()
    logger.warning(
        "LLM_PROVIDER='%s' no reconocido; usando Ollama por defecto.", provider
    )
    return OllamaChatProvider()


def embedding_provider_factory():
    """Construye el embedding provider (Ollama es el único soportado)."""
    return OllamaEmbeddingProvider()