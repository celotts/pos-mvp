"""Paquete de IA desacoplado: puertos, proveedores, tools planas y driver de agentes."""

from service.ai.agent_service import AgentService
from service.ai.driver import LangGraphAgentDriver
from service.ai.factory import ai_service, build_agent_service
from service.ai.ports import IChatProvider, IEmbeddingProvider, ToolDef

__all__ = [
    "AgentService",
    "IChatProvider",
    "IEmbeddingProvider",
    "LangGraphAgentDriver",
    "ToolDef",
    "ai_service",
    "build_agent_service",
]