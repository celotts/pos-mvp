"""Helper de auditoría (C.4): registra operaciones sensibles en `audit_log`."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.tenancy import get_current_tenant
from models.audit_log import AuditLog


def _serialize(value: Any) -> str | None:
    """Serializa el payload a texto corto para `details` sin exponer secretos."""
    if value is None:
        return None
    try:
        return str(value)[:2000]
    except Exception:  # noqa: BLE001 - nunca debe romper la operación principal
        return "<unserializable>"


async def record_audit(
    db: AsyncSession,
    *,
    actor_id: Any | None,
    actor_email: str | None,
    entity: str,
    entity_id: Any | None,
    action: str,
    ip: str | None = None,
    details: Any | None = None,
    commit: bool = False,
) -> None:
    """Inserta una fila en `audit_log`. `commit=False` por defecto para que la
    transacción principal controle el flush/rollback junto con su operación."""
    entry = AuditLog(
        tenant_id=get_current_tenant(),
        actor_id=str(actor_id) if actor_id else None,
        actor_email=actor_email,
        entity=entity,
        entity_id=str(entity_id) if entity_id else None,
        action=action,
        ip=ip,
        details=_serialize(details),
    )
    db.add(entry)
    if commit:
        await db.commit()
