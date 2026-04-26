# NeuroScanAD — EEG Alzheimer's Detection

Full-stack web application for resting-state EEG analysis to identify Alzheimer's Disease.

## Project Structure

```
eeg-alzheimer-app/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── requirements.txt    # Python dependencies
│   └── README.md
└── frontend/
    ├── public/index.html
    ├── package.json
    └── src/
        ├── App.js / App.css
        ├── utils/api.js
        └── pages/
            ├── Dashboard.js
            ├── SubjectAnalysis.js
            ├── ComparisonView.js
            └── BatchView.js
```

## Quick Start

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATASET_ROOT=/path/to/ds004504
python app.py
# → http://localhost:5000
```

### 2. Frontend
```bash
cd frontend
npm install
npm start
# → http://localhost:3000
```

## Features

| Page | Description |
|------|-------------|
| **Dashboard** | Dataset overview, subject groups, biomarker explanations |
| **Subject Analysis** | Single-subject EEG analysis with waveform, band powers, per-channel table, risk scores |
| **Comparison** | Side-by-side comparison of 2–6 subjects with bar charts and score table |
| **Batch Stats** | Group-level aggregate statistics with mean ± SD across AD/FTD/CN |

## EEG Biomarkers

| Biomarker | Formula | AD Threshold |
|-----------|---------|-------------|
| Theta/Alpha Ratio | θ / α | > 1.5 = elevated |
| Delta/Alpha Ratio | δ / α | > 2.0 = high risk |
| Brain Cognitive Score (BCS) | (δ+θ) / (α+β) | Higher = worse |
| Alpha3/Alpha2 Ratio | α3 / α2 | > 1.35 = MCI→AD |

## Dataset

- **88 subjects**: 36 AD, 23 FTD, 29 CN
- **19 channels**: 10-20 system (Fp1, Fp2, F7, F3, Fz, F4, F8, T3, C3, Cz, C4, T4, T5, P3, Pz, P4, T6, O1, O2)
- **500 Hz sampling rate**, eyes-closed resting state
- Source: AHEPA General Hospital, Thessaloniki

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/subjects` | GET | All 88 subjects with group labels |
| `/api/analyze/<id>` | GET | Full analysis for one subject |
| `/api/compare` | POST | Compare 2–6 subjects |
| `/api/batch` | POST | Group-level statistics |
| `/api/waveform/<id>` | GET | EEG waveform snippet |
