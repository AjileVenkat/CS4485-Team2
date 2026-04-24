"""Backend API tests for health and prediction contracts."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app  # noqa: E402


class BackendApiTests(unittest.TestCase):
    def test_health_endpoint(self):
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("status"), "ok")
        self.assertIn("model", payload)
        self.assertIn("upload", payload)

    def test_predict_from_feature_csv(self):
        with TestClient(app) as client:
            feature_names = app.state.model_service.feature_names
            self.assertTrue(feature_names, "Model feature names should be available")

            sample_row = {name: 0.0 for name in feature_names}
            csv_buffer = io.StringIO()
            pd.DataFrame([sample_row]).to_csv(csv_buffer, index=False)

            response = client.post(
                "/predict",
                files={"file": ("sample_features.csv", csv_buffer.getvalue(), "text/csv")},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload.get("status"), "success")
        self.assertIn(payload.get("prediction"), ("AD", "HC", "FTD"))
        self.assertIsInstance(payload.get("risk_score"), (int, float))

        all_probs = payload.get("all_probs", {})
        self.assertIn("AD", all_probs)
        self.assertIn("HC", all_probs)
        self.assertIn("FTD", all_probs)

        insights = payload.get("insights", [])
        self.assertIsInstance(insights, list)

    def test_predict_rejects_unsupported_extension(self):
        with TestClient(app) as client:
            response = client.post(
                "/predict",
                files={"file": ("malware.exe", b"not_eeg", "application/octet-stream")},
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.json().get("detail", ""))


if __name__ == "__main__":
    unittest.main()
