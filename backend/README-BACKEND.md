# Backend Setup and Run

## 0) Activate virtual environment (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

## 1) Install dependencies

From the `backend` folder:

```powershell
pip install -r requirements.txt
```

## 2) Download OpenNeuro metadata

This project now includes a downloader script using `openneuro-py`:

```powershell
python download_openneuro_dataset.py --dataset ds004504 --target-dir ds004504
```


## 2b) Download full EEG files (`.set` / `.fdt`)

OpenNeuro stores EEG signal files as git-annex objects. Install `git-annex` first:

- https://downloads.kitenet.net/git-annex/windows/current/git-annex-installer.exe

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\download_openneuro_full.ps1
```

## 3) (Optional) Rebuild feature matrix from dataset

```powershell
Set-Location model
python final_feat_matrix.py
Set-Location ..
```

The script looks for dataset files under `backend/ds004504` or `backend/ds004504_annex`.

## 4) (Optional) Retrain random forest model

```powershell
Set-Location model
python rf.py
Set-Location ..
```

This writes `alzheimers_model.joblib` in `backend/model`.

## 5) Run FastAPI backend

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- API docs: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

## 6) API contract used by the frontend

- `POST /predict`
	- Upload form-data field: `file`
	- Supported formats: `.set`, `.edf`, `.fif`, `.csv`, `.txt`
	- Returns: `status`, `prediction`, `risk_score`, `all_probs`, `insights`

- `GET /health`
	- Returns service and model metadata for monitoring.

## 7) Backend structure

The backend is organized into:

- `app/api/routes/` for endpoints
- `app/services/` for parsing, feature extraction, model inference, and insights
- `app/schemas/` for API response models
- `app/core/` for settings and constants

`main.py` remains the entrypoint (`uvicorn main:app`) and imports the organized app package.
