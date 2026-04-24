"""Model loading and prediction utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

from app.core.constants import GROUP_TO_LABEL, LABEL_ORDER


class ModelService:
    """Wraps the trained classifier and handles feature alignment and prediction."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.model = joblib.load(model_path)
        self.feature_names = self._discover_feature_names()
        self.class_labels = self._discover_class_labels()

    def _discover_feature_names(self) -> List[str]:
        names = getattr(self.model, "feature_names_in_", None)
        if names is None and hasattr(self.model, "named_steps"):
            for step in self.model.named_steps.values():
                step_features = getattr(step, "feature_names_in_", None)
                if step_features is not None:
                    names = step_features
                    break

        if names is None:
            return []

        return [str(name) for name in names]

    @staticmethod
    def _normalize_label(raw_label: object) -> str:
        if isinstance(raw_label, (np.integer, int, float)):
            candidate = GROUP_TO_LABEL.get(int(raw_label))
            if candidate:
                return candidate

        text = str(raw_label).strip().upper()
        if text in ("HC", "HEALTHY", "HEALTHY CONTROL"):
            return "HC"
        if text in ("AD", "ALZHEIMERS", "ALZHEIMER'S"):
            return "AD"
        if text in ("FTD", "FRONTOTEMPORAL DEMENTIA"):
            return "FTD"
        return text

    def _discover_class_labels(self) -> List[str]:
        classes = getattr(self.model, "classes_", None)
        if classes is None and hasattr(self.model, "named_steps"):
            for step in reversed(list(self.model.named_steps.values())):
                step_classes = getattr(step, "classes_", None)
                if step_classes is not None:
                    classes = step_classes
                    break

        if classes is None:
            return list(LABEL_ORDER)

        return [self._normalize_label(class_item) for class_item in classes]

    def align_features(self, feature_frame: pd.DataFrame) -> pd.DataFrame:
        """Align incoming feature frame to model expectations."""
        aligned = feature_frame.copy()
        aligned = aligned.apply(pd.to_numeric, errors="coerce").fillna(0.0)

        if not self.feature_names:
            return aligned

        for column in self.feature_names:
            if column not in aligned.columns:
                aligned[column] = 0.0

        return aligned[self.feature_names]

    @staticmethod
    def _normalize_probability_map(probabilities: Dict[str, float]) -> Dict[str, float]:
        normalized = {label: max(0.0, float(probabilities.get(label, 0.0))) for label in LABEL_ORDER}
        total = sum(normalized.values())
        if total <= 0:
            return {label: 0.0 for label in LABEL_ORDER}

        return {label: value / total for label, value in normalized.items()}

    def predict(self, feature_frame: pd.DataFrame) -> Tuple[str, Dict[str, float], float]:
        """Run model inference and return top class, class probabilities, and risk score."""
        aligned = self.align_features(feature_frame)

        raw_prediction = self.model.predict(aligned)[0]
        predicted_label = self._normalize_label(raw_prediction)

        if hasattr(self.model, "predict_proba"):
            raw_probabilities = self.model.predict_proba(aligned)[0]
            probability_map = {
                label: float(prob)
                for label, prob in zip(self.class_labels, raw_probabilities)
            }
        else:
            probability_map = {label: 0.0 for label in self.class_labels}
            if predicted_label in probability_map:
                probability_map[predicted_label] = 1.0

        all_probs = self._normalize_probability_map(probability_map)
        top_label = max(all_probs, key=all_probs.get)
        risk_score = round(all_probs[top_label] * 100.0, 2)

        return top_label, all_probs, risk_score
