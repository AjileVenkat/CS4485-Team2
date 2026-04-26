# EEG AD Detection — Backend

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Dataset Configuration

Set the path to your BIDS dataset root:

```bash
export DATASET_ROOT=/path/to/ds004504
```

Or on Windows:
```cmd
set DATASET_ROOT=C:\path\to\ds004504
```

The API defaults to looking for `ds004504/` in the current working directory.

## Run

```bash
python app.py
```

Server starts on `http://localhost:5000`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/subjects` | List all 88 subjects with group labels |
| GET | `/api/analyze/<subject_id>` | Full analysis for one subject |
| POST | `/api/compare` | Side-by-side comparison of 2–6 subjects |
| POST | `/api/batch` | Aggregate stats for a group (AD/FTD/CN) |
| GET | `/api/waveform/<subject_id>` | Downsampled EEG waveform snippet |

### Example: Analyze subject 001

```bash
curl http://localhost:5000/api/analyze/sub-001
```

### Example: Compare AD vs CN

```bash
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"subjects": ["sub-001", "sub-065"]}'
```
