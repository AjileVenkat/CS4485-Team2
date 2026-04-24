"""Runtime settings for the FastAPI backend."""

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    """Application configuration loaded from environment and defaults."""

    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    model_candidates: tuple[str, ...] = (
        "alzheimers_model.joblib",
        "final_ad_model.joblib",
        "alzheimers_model_v2.joblib",
    )
    allowed_extensions: tuple[str, ...] = (".set", ".edf", ".fif", ".csv", ".txt")
    max_upload_size_mb: int = 50
    cors_origins: tuple[str, ...] = ("*",)
    model_dir: Path = field(init=False)
    temp_upload_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "model_dir", self.base_dir / "model")
        object.__setattr__(self, "temp_upload_dir", self.base_dir / "uploads_tmp")

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def resolve_model_path(self) -> Path:
        """Resolve model path, honoring MODEL_PATH if provided."""
        override = os.getenv("MODEL_PATH")
        if override:
            model_path = Path(override)
            if model_path.exists():
                return model_path.resolve()
            raise FileNotFoundError(f"MODEL_PATH points to a missing file: {model_path}")

        for candidate in self.model_candidates:
            candidate_path = self.model_dir / candidate
            if candidate_path.exists():
                return candidate_path

        looked_in = ", ".join(str(self.model_dir / item) for item in self.model_candidates)
        raise FileNotFoundError(f"No model file found. Tried: {looked_in}")
