# AGENT.MD: Contexto, Arquitectura y Reglas de Desarrollo para pos-API

## 5. Validación de Datos en Endpoints
```python
# api/deps.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class PaginatedRequest(BaseRequestModel):
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None

class FilterRequest(BaseRequestModel):
    category: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None