from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import mne
import pandas as pd
import os

try:
    from model.final_feat_matrix import feature_extraction
except ModuleNotFoundError:
    from backend.model.final_feat_matrix import feature_extraction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "alzheimers_model.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

@app.post("/predict")
async def predict_eeg(file: UploadFile = File(...)):
    safe_name = Path(file.filename).name
    temp_path = BASE_DIR / f"temp_{safe_name}"
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        raw = mne.io.read_raw_eeglab(str(temp_path), preload=True, verbose=False)
        raw.set_eeg_reference(ref_channels='average', verbose=False)
        raw.filter(l_freq=0.5, h_freq=45, method='iir', iir_params=dict(order=2, ftype='butter'), phase='zero', verbose=False)
        raw.resample(128, verbose=False)

        if raw.times[-1] < 4:
            raise HTTPException(status_code=400, detail="EEG file must contain at least 4 seconds of data")

        data_ep = raw.copy().crop(tmin=0, tmax=4 - 1 / 128, verbose=False).get_data()

        features = feature_extraction(data_ep, "User_Patient", {"Age": 63, "Gender": "M"}, 128)
        df = pd.DataFrame([features]).drop(columns=['Subject_ID'], errors='ignore')

        expected_cols = getattr(model, "feature_names_in_", None)
        if expected_cols is None and hasattr(model, "named_steps"):
            for step in model.named_steps.values():
                expected_cols = getattr(step, "feature_names_in_", None)
                if expected_cols is not None:
                    break

        if expected_cols is not None:
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = 0.0
            df = df[list(expected_cols)]


        pred = int(model.predict(df)[0])
        probability = model.predict_proba(df)[0].tolist()

        labels = ["Healthy", "FTD", "AD"]

        return {
            "status": "success",
            "prediction": labels[pred],
            "risk_score": round(max(probability) * 100, 2),
            "all_probs": dict(zip(labels, probability))
        }

    finally:
        if temp_path.exists():
            os.remove(temp_path)