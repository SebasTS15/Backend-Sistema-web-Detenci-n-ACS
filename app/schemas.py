from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    usuario_id: int | None = None
    paciente_id: str | None = None
    signals: list[list[float]] = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    normalize: bool = True
    guardar_resultado: bool = True
    guardar_historial: bool = True


class PredictResponse(BaseModel):
    prediccion: bool
    probabilidad: float
    clase: str
    threshold: float
    modelo: str
    preprocessing: dict[str, Any]
    resultado_id: int | None = None
    historial_id: int | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
    model_loaded: bool
