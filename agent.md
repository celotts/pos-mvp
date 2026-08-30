# AGENT.MD: Contexto, Arquitectura y Reglas de Desarrollo para pos-API

> **DIRECTIVA PRIMARIA PARA EL AGENTE DE IA:**
>
> 1. Queda **ESTRICTAMENTE PROHIBIDO** alterar la estructura de carpetas existente, refactorizar archivos funcionando sin autorización explícita o introducir código especulativo/no solicitado.
> 2. Cada respuesta debe ser directa, certera y alineada 100% con los patrones del proyecto. No agregues "mejoras" fuera del alcance de la solicitud actual.
>
>
> ---

## 1. Contexto General del Proyecto

**pos-API** es un backend en Python encargado de gestionar las operaciones centrales de un sistema Punto de Venta (POS). Posee un módulo especializado de **IA y Agentes** para interactuar con la base de datos (SQL dinámico/RAG con `pgvector`), generar análisis de inventario/ventas en tiempo real y ejecutar tareas operativas vía llamadas a herramientas (*Tool Calling*).

---

## 2. Pila Tecnológica (Tech Stack)

* **Lenguaje:** Python 3.11+
* **Framework Web:** FastAPI (Arquitectura asíncrona con `async`/`await`)
* **Base de Datos Relacional:** PostgreSQL + Extensión `pgvector`
* **ORM & Persistencia:** SQLAlchemy 2.0 (Async Session) + Pydantic v2
* **Capa de Negocio:** Patrón de Capas (`Controller` -> `Service` -> `CRUD` -> `Model`)
* **Motor IA:** LangChain / LangGraph / OpenAI API / Ollama nativo (`agent_tools.py`, `ai_agent_service.py`, `llm_service.py`)

---

## 3. Estructura Real del Repositorio (INMUTABLE)

El agente debe **respetar y mantener esta estructura exacta**. Queda prohibido crear carpetas alternativas (como `app/` o `infrastructure/`) o mover archivos de sus directorios actuales.

```text
.
├── api/                           # Capa de Entrada HTTP (Endpoints & Handlers)
│   ├── endpoints/                 # Controladores por dominio
│   │   ├── assistant_controller.py
│   │   ├── inventory_controller.py
│   │   ├── product_controller.py
│   │   ├── sale_controller.py
│   │   └── ... (otros controladores)
│   ├── deps.py                    # Inyección de dependencias general
│   ├── deps_auth.py               # Inyección de dependencias de autenticación
│   ├── exception_handlers.py      # Captura centralizada de excepciones
│   └── response_factory.py        # Fábrica de respuestas HTTP estandarizadas
├── core/                          # Configuración Base, Seguridad y Acceso a Datos
│   ├── base.py                    # Base de modelos SQLAlchemy
│   ├── config.py                  # Variables de entorno (Pydantic Settings)
│   ├── db.py                      # Conexión y sesión Async de BD
│   ├── security.py                # Hash de contraseñas y JWT
│   └── crud_*.py                  # Operaciones directas a BD (crud_base, crud_sale, etc.)
├── models/                        # Entidades ORM de SQLAlchemy
│   ├── sales_vector.py            # Tabla de embeddings/vectores pgvector
│   ├── sale.py
│   ├── product.py
│   └── ... (modelos de entidad)
├── schemas/                       # Validación de datos (Pydantic Models)
│   ├── assistant.py
│   ├── inventory_analysis.py
│   └── ... (esquemas DTOs)
├── service/                       # Lógica de Negocio y Módulo de IA
│   ├── agent_tools.py             # Herramientas expuestas al agente de IA
│   ├── ai_agent_service.py        # Orquestación del Agente de IA
│   ├── ai_service.py              # Servicio principal de IA/RAG
│   ├── llm_service.py             # Cliente y conexión directa con el LLM
│   ├── inventory_analisis_service.py
│   └── ... (servicios de negocio por entidad)
├── utils/                         # Utilidades generales
│   └── logger.py                  # Configuración de logs
├── test/                          # Pruebas unitarias y de integración
├── dependencies.py                # Dependencias raíz
├── generate_sales.py              # Scripts de utilidad
├── initial_data.py                # Poblamiento inicial de datos
└── main.py                        # Punto de entrada de FastAPI
```
