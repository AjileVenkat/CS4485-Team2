"""Shared constants for EEG parsing and model class labels."""

REQUIRED_CHANNELS = [
    "Fp1",
    "Fp2",
    "F3",
    "F4",
    "C3",
    "C4",
    "P3",
    "P4",
    "O1",
    "O2",
    "F7",
    "F8",
    "T3",
    "T4",
    "T5",
    "T6",
    "Fz",
    "Cz",
    "Pz",
]

CHANNEL_ALIASES = {
    "T3": ["T7"],
    "T4": ["T8"],
    "T5": ["P7"],
    "T6": ["P8"],
}

DEFAULT_SAMPLING_RATE = 128
MIN_SECONDS_REQUIRED = 4

GROUP_TO_LABEL = {
    0: "HC",
    1: "FTD",
    2: "AD",
}

LABEL_ORDER = ("AD", "HC", "FTD")
