from api.endpoints import login, roles, users
from api.exception_handlers import http_exception_handler
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Medical Appointments RAG API",
    description="API para la gestión de citas médicas con capacidades de Búsqueda Aumentada por Generación (RAG).",
    version="0.1.0",
)

# Registra el manejador de excepciones personalizado
app.add_exception_handler(HTTPException, http_exception_handler)


# @app.on_event("startup")
# async def on_startup():
#     # Ejecuta la lógica de inicialización en el arranque
#     # (crea tablas y el primer superusuario si no existen)
#     await init_db()


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(login, prefix="/api/v1", tags=["Boostrap & Auth"])
app.include_router(users, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles, prefix="/api/v1/roles", tags=["Roles"])
