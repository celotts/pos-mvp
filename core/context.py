import contextvars
import uuid

# Variable de contexto para almacenar el ID del usuario actual
# Esto permite que el ID viaje a través de las llamadas asíncronas.
current_user_id_var: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar[
    uuid.UUID | None
]("current_user_id", default=None)


def set_user_context(user_id: uuid.UUID) -> contextvars.Token:
    """Establece el ID del usuario en el contexto actual y retorna un token para revertirlo."""
    token = current_user_id_var.set(user_id)
    return token


def get_current_user_id() -> uuid.UUID | None:
    """Recupera el ID del usuario del contexto actual."""
    return current_user_id_var.get()


def clear_user_context():
    """Limpia el contexto del usuario al finalizar la solicitud."""
    current_user_id_var.reset(None)
