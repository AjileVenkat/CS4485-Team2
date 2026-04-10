from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import joblib
import mne
import pandas as pd
import os
from backend.model.final_feat_matrix import features_extraction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("alzheimers_model.joblib")

@app.post("/predict")
async def predict_eeg(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        raw = mne.io.read_raw_eeglab(temp_path, preload=True, verbose=False)
        data_ep = raw.get_data(tmin=0, tmax=4)

        features = features_extraction(data_ep, "User_Patient", None, 128)
        df = pd.DataFrame([features]).drop(columns=['Subject_ID'])

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
        if os.path.exists(temp_path):
            os.remove(temp_path)