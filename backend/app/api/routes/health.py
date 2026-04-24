"""Health and service metadata routes."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["System"])


@router.get("/health")
def health(request: Request):
    settings = request.app.state.settings
    model_service = request.app.state.model_service

    return {
        "status": "ok",
        "model": {
            "name": model_service.model_path.name,
            "path": str(model_service.model_path),
            "feature_count": len(model_service.feature_names),
            "class_labels": model_service.class_labels,
        },
        "upload": {
            "allowed_extensions": list(settings.allowed_extensions),
            "max_upload_size_mb": settings.max_upload_size_mb,
        },
    }
