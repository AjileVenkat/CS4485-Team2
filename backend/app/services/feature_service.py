"""Transforms EEG data into model-ready feature rows."""

from __future__ import annotations

import pandas as pd

try:
    from model.final_feat_matrix import feature_extraction
except ModuleNotFoundError:
    from backend.model.final_feat_matrix import feature_extraction


def build_feature_frame(eeg_data, sampling_rate):
    """Extract features from EEG epoch data and return a one-row DataFrame."""
    features = feature_extraction(
        eeg_data,
        "Uploaded_Subject",
        None,
        sampling_rate,
    )

    return pd.DataFrame([features]).drop(columns=["Subject_ID"], errors="ignore")
