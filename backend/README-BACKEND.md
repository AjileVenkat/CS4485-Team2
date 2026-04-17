# Backend Setup and Run

## 0) Activate virtual environment (Windows PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
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

Notes:
- This downloads top-level BIDS metadata files.
- Re-running the same command resumes interrupted downloads.

## 2b) Download full EEG files (`.set` / `.fdt`)

OpenNeuro stores EEG signal files as git-annex objects. Install `git-annex` first:

- https://downloads.kitenet.net/git-annex/windows/current/git-annex-installer.exe

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\download_openneuro_full.ps1
```

This clones into `backend/ds004504_annex`, checks out snapshot `1.0.8`, enables the `s3-PUBLIC` remote, and runs `git-annex get .`.

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

Upload an EEGLAB `.set` file to `/predict`.
