"""Inference routes for EEG classification."""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.schemas.prediction import PredictionResponse
from app.services.feature_service import build_feature_frame
from app.services.insight_service import generate_insights
from app.services.upload_parser import parse_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Inference"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    """Run model inference from uploaded EEG or feature tabular files."""
    settings = request.app.state.settings
    model_service = request.app.state.model_service

    file_name = (file.filename or "upload").strip()
    suffix = Path(file_name).suffix.lower()

    if not suffix:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must include an extension.")

    if suffix not in settings.allowed_extensions:
        allowed = ", ".join(settings.allowed_extensions)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix}'. Allowed extensions: {allowed}",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds {settings.max_upload_size_mb} MB limit.",
        )

    settings.temp_upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None

    try:
        with NamedTemporaryFile(
            mode="wb",
            suffix=suffix,
            prefix="upload_",
            dir=settings.temp_upload_dir,
            delete=False,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = Path(temp_file.name)

        parsed_upload = parse_upload_file(temp_path, model_service)
        if parsed_upload.feature_frame is not None:
            feature_frame = parsed_upload.feature_frame
        elif parsed_upload.eeg_data is not None:
            feature_frame = build_feature_frame(parsed_upload.eeg_data, parsed_upload.sampling_rate)
        else:
            raise ValueError("Could not parse upload into features or EEG signal data.")

        prediction, all_probs, risk_score = model_service.predict(feature_frame)
        feature_values = feature_frame.iloc[0].to_dict() if not feature_frame.empty else {}
        insights = generate_insights(feature_values, all_probs, prediction, risk_score)

        return PredictionResponse(
            status="success",
            prediction=prediction,
            risk_score=risk_score,
            all_probs=all_probs,
            insights=insights,
        )

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unhandled inference failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {exc}",
        ) from exc
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
