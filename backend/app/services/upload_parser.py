"""Parses uploaded files into either feature frames or EEG matrices."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mne
import numpy as np
import pandas as pd

from app.core.constants import (
    CHANNEL_ALIASES,
    DEFAULT_SAMPLING_RATE,
    MIN_SECONDS_REQUIRED,
    REQUIRED_CHANNELS,
)
from app.services.model_service import ModelService


@dataclass
class ParsedUpload:
    feature_frame: Optional[pd.DataFrame] = None
    eeg_data: Optional[np.ndarray] = None
    sampling_rate: int = DEFAULT_SAMPLING_RATE


def parse_upload_file(file_path: Path, model_service: ModelService) -> ParsedUpload:
    """Parse any supported upload into a model-ready representation."""
    suffix = file_path.suffix.lower()

    if suffix in (".set", ".edf", ".fif"):
        eeg_data, sfreq = _parse_eeg_file(file_path, suffix)
        return ParsedUpload(eeg_data=eeg_data, sampling_rate=sfreq)

    if suffix in (".csv", ".txt"):
        return _parse_tabular_file(file_path, suffix, model_service)

    raise ValueError(f"Unsupported file extension: {suffix}")


def _parse_eeg_file(file_path: Path, suffix: str):
    if suffix == ".set":
        raw = mne.io.read_raw_eeglab(str(file_path), preload=True, verbose=False)
    elif suffix == ".edf":
        raw = mne.io.read_raw_edf(str(file_path), preload=True, verbose=False)
    elif suffix == ".fif":
        raw = mne.io.read_raw_fif(str(file_path), preload=True, verbose=False)
    else:
        raise ValueError(f"Unsupported EEG file extension: {suffix}")

    raw = _normalize_channels(raw)
    raw = _preprocess_raw(raw)

    duration_seconds = raw.n_times / float(raw.info["sfreq"])
    if duration_seconds < MIN_SECONDS_REQUIRED:
        raise ValueError("EEG file must contain at least 4 seconds of data.")

    sfreq = int(round(raw.info["sfreq"]))
    window = raw.copy().crop(tmin=0.0, tmax=MIN_SECONDS_REQUIRED - (1.0 / sfreq), verbose=False)
    eeg_data = window.get_data()
    return eeg_data, sfreq


def _normalize_channels(raw):
    """Rename aliases and ensure required channels are present and ordered."""
    available = list(raw.ch_names)
    rename_map = {}

    for target, aliases in CHANNEL_ALIASES.items():
        if _find_channel(available, target):
            continue

        for alias in aliases:
            alias_name = _find_channel(available, alias)
            if alias_name:
                rename_map[alias_name] = target
                available = [target if name == alias_name else name for name in available]
                break

    if rename_map:
        raw.rename_channels(rename_map)

    missing = [channel for channel in REQUIRED_CHANNELS if _find_channel(raw.ch_names, channel) is None]
    if missing:
        raise ValueError(
            "Uploaded EEG is missing required channels: " + ", ".join(missing)
        )

    ordered_names = [_find_channel(raw.ch_names, channel) for channel in REQUIRED_CHANNELS]
    raw.pick(ordered_names)

    return raw


def _preprocess_raw(raw):
    raw.set_eeg_reference(ref_channels="average", verbose=False)

    high_cut = min(45.0, (float(raw.info["sfreq"]) / 2.0) - 1.0)
    if high_cut <= 0.5:
        raise ValueError("Sampling rate is too low for required preprocessing.")

    raw.filter(
        l_freq=0.5,
        h_freq=high_cut,
        method="iir",
        iir_params={"order": 2, "ftype": "butter"},
        phase="zero",
        verbose=False,
    )

    raw.resample(DEFAULT_SAMPLING_RATE, verbose=False)
    return raw


def _parse_tabular_file(file_path: Path, suffix: str, model_service: ModelService) -> ParsedUpload:
    frame = _read_tabular(file_path, suffix)
    if frame.empty:
        raise ValueError("Tabular upload is empty.")

    feature_frame = _try_parse_feature_frame(frame, model_service)
    if feature_frame is not None:
        return ParsedUpload(feature_frame=feature_frame, sampling_rate=DEFAULT_SAMPLING_RATE)

    eeg_data = _try_parse_eeg_matrix(frame)
    if eeg_data is None:
        raise ValueError(
            "Tabular upload must include model feature columns or a 19-channel EEG matrix."
        )

    if eeg_data.shape[1] < (DEFAULT_SAMPLING_RATE * MIN_SECONDS_REQUIRED):
        raise ValueError("Tabular EEG upload must include at least 512 samples (4 seconds at 128 Hz).")

    eeg_window = eeg_data[:, : DEFAULT_SAMPLING_RATE * MIN_SECONDS_REQUIRED]
    return ParsedUpload(eeg_data=eeg_window, sampling_rate=DEFAULT_SAMPLING_RATE)


def _read_tabular(file_path: Path, suffix: str) -> pd.DataFrame:
    if suffix == ".csv":
        return pd.read_csv(file_path)

    try:
        return pd.read_csv(file_path, sep=None, engine="python")
    except Exception:
        return pd.read_csv(file_path, sep=r"\s+", header=None, engine="python")


def _try_parse_feature_frame(frame: pd.DataFrame, model_service: ModelService) -> Optional[pd.DataFrame]:
    cleaned = frame.copy()
    cleaned = cleaned.drop(columns=["Subject_ID", "Group"], errors="ignore")

    if model_service.feature_names:
        overlap = [column for column in cleaned.columns if column in model_service.feature_names]
        if len(overlap) >= 3:
            return cleaned.head(1)

    numeric = cleaned.apply(pd.to_numeric, errors="coerce")
    numeric = numeric.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if numeric.empty or not model_service.feature_names:
        return None

    values = numeric.to_numpy(dtype=float)

    if values.shape == (1, len(model_service.feature_names)):
        return pd.DataFrame(values, columns=model_service.feature_names)

    if values.shape == (len(model_service.feature_names), 1):
        return pd.DataFrame([values[:, 0]], columns=model_service.feature_names)

    return None


def _try_parse_eeg_matrix(frame: pd.DataFrame) -> Optional[np.ndarray]:
    numeric = frame.apply(pd.to_numeric, errors="coerce")
    numeric = numeric.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if numeric.empty:
        return None

    matrix = numeric.to_numpy(dtype=float)
    expected_channels = len(REQUIRED_CHANNELS)

    if matrix.ndim != 2:
        return None

    if matrix.shape[0] == expected_channels:
        return matrix

    if matrix.shape[1] == expected_channels:
        return matrix.T

    return None


def _find_channel(ch_names, target_name: str) -> Optional[str]:
    target_upper = target_name.strip().upper()
    for channel in ch_names:
        if channel.strip().upper() == target_upper:
            return channel
    return None
