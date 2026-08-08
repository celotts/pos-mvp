from fastapi import FastAPI

from api.endpoints import login, users
from initial_data import main as init_db

app = FastAPI(
    title="Medical Appointments RAG API",
    description="API para la gestión de citas médicas con capacidades de Búsqueda Aumentada por Generación (RAG).",
    version="0.1.0",
)


@app.on_event("startup")
async def on_startup():
    # Ejecuta la lógica de inicialización en el arranque
    # (crea tablas y el primer superusuario si no existen)
    await init_db()


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(login.router, prefix="/api/v1", tags=["Login"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
