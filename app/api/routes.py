from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.repositories import (
    check_database,
    get_usuario,
    insert_historial_consulta,
    insert_resultado,
    list_historial_by_usuario,
    list_resultados_by_usuario,
)
from app.db.session import get_db
from app.ml.service import get_model_service
from app.schemas import HealthResponse, PredictRequest, PredictResponse
from app.schemas import ErrorResponse


router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    database_status = "ok"
    try:
        check_database(db)
    except SQLAlchemyError:
        database_status = "error"

    model_loaded = True
    try:
        get_model_service()
    except Exception:
        model_loaded = False

    return HealthResponse(status="ok", database=database_status, model_loaded=model_loaded)


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, str] = Depends(get_current_user),
) -> PredictResponse:
    if payload.usuario_id is not None and get_usuario(db, payload.usuario_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    try:
        prediction = get_model_service().predict(
            payload.signals,
            normalize=payload.normalize,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error ejecutando el modelo: {exc}") from exc

    response_data: dict[str, Any] = {**prediction, "resultado_id": None, "historial_id": None}

    try:
        if payload.guardar_resultado:
            response_data["resultado_id"] = insert_resultado(
                db,
                usuario_id=payload.usuario_id,
                paciente_id=payload.paciente_id,
                prediccion=prediction["prediccion"],
                probabilidad=prediction["probabilidad"],
                clase=prediction["clase"],
                modelo=prediction["modelo"],
                metadata={**payload.metadata, "preprocessing": prediction["preprocessing"]},
            )

        if payload.guardar_historial:
            response_data["historial_id"] = insert_historial_consulta(
                db,
                usuario_id=payload.usuario_id,
                endpoint="/api/v1/predict",
                request=payload.model_dump(exclude={"signals"}),
                response=response_data,
            )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error guardando en PostgreSQL: {exc}") from exc

    return PredictResponse(**response_data)


@router.get(
    "/usuarios/{usuario_id}",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    data = get_usuario(db, usuario_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return data


@router.get(
    "/usuarios/{usuario_id}/resultados",
    responses={401: {"model": ErrorResponse}},
)
def resultados_usuario(
    usuario_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict[str, str] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    return list_resultados_by_usuario(db, usuario_id, limit=limit)


@router.get(
    "/usuarios/{usuario_id}/historial",
    responses={401: {"model": ErrorResponse}},
)
def historial_usuario(
    usuario_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict[str, str] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    return list_historial_by_usuario(db, usuario_id, limit=limit)
