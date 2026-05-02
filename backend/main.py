from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import joblib
import mne
import pandas as pd
import os
import uuid
import numpy as np

from model.final_feat_matrix import features_extraction

app = FastAPI(title="Alzheimer EEG Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "final_ad_model.joblib"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"{MODEL_PATH} not found")

model = joblib.load(MODEL_PATH)

LABELS = ["Healthy", "FTD", "AD"]


@app.get("/")
def root():
    return {"message": "Alzheimer EEG Prediction API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict_eeg(
    file: UploadFile = File(...),
    age: int = Form(...),
    gender: int = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    temp_path = f"temp_{uuid.uuid4()}_{file.filename}"

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        with open(temp_path, "wb") as buffer:
            buffer.write(contents)

        # Read EEG file
        raw = mne.io.read_raw_eeglab(
            temp_path,
            preload=True,
            verbose=False
        )
        
        raw.set_eeg_reference(ref_channels='average', verbose=False)

        raw.filter(
            l_freq=0.5,
            h_freq=45,
            method='iir',
            iir_params=dict(order=2, ftype='butter'),
            phase='zero',
            verbose=False
        )

        raw.resample(128, verbose=False)

        # Match training: split EEG into 4-second epochs and average predictions
        duration = min(60, int(raw.times[-1]))
        step = 4

        all_probabilities = []

        for start in range(0, duration - step + 1, step):
            stop = start + step

            raw_ep = raw.copy().crop(
                tmin=start,
                tmax=stop - 1 / 128,
                verbose=False
            )

            data_ep = raw_ep.get_data()

            features = features_extraction(
                data_ep,
                "User_Patient",
                None,
                128
            )

            df = pd.DataFrame([features])

            if "Subject_ID" in df.columns:
                df = df.drop(columns=["Subject_ID"])

            df["Age"] = age
            df["Gender"] = gender

            probs = model.predict_proba(df)[0]
            all_probabilities.append(probs)

        if not all_probabilities:
            raise HTTPException(status_code=400, detail="EEG file is too short. Need at least 4 seconds.")

        avg_probability = np.mean(all_probabilities, axis=0)
        pred = int(np.argmax(avg_probability))
        probability = avg_probability.tolist()

        return {
            "status": "success",
            "prediction": LABELS[pred],
            "risk_score": round(max(probability) * 100, 2),
            "all_probs": {
                label: round(float(prob) * 100, 2)
                for label, prob in zip(LABELS, probability)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
