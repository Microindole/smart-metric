from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from core.estimate_metric import calculate_estimate  # noqa: E402
from core.oo_metric import analyze_oo_files  # noqa: E402


class OoMetricTests(unittest.TestCase):
    def test_analyzes_java_ck_lk_metrics(self):
        source = b"""
        class Base {
            private int id;
            public int getId() { return id; }
        }
        class User extends Base {
            private int score;
            public void login(String password) {
                if (password != null && password.length() > 6) {
                    score++;
                }
            }
            public int getScore() { return score; }
        }
        """

        result = analyze_oo_files([{"filename": "User.java", "content": source}])

        self.assertEqual(result["summary"]["class_count"], 2)
        user = next(item for item in result["classes"] if item["class_name"] == "User")
        self.assertEqual(user["parent"], "Base")
        self.assertEqual(user["ck"]["dit"], 1)
        self.assertGreaterEqual(user["ck"]["wmc"], 3)
        self.assertEqual(user["lk"]["nom"], 2)


class EstimateMetricTests(unittest.TestCase):
    def test_calculates_effort_cost_duration(self):
        result = calculate_estimate(
            {
                "metric_type": "fp",
                "metric_value": 100,
                "productivity": 8,
                "hours_per_person_month": 160,
                "cost_per_person_month": 12000,
                "team_size": 4,
            }
        )

        self.assertEqual(result["effort_hours"], 800)
        self.assertEqual(result["effort_person_months"], 5)
        self.assertEqual(result["cost"], 60000)
        self.assertEqual(result["duration_months"], 1.25)


class OoEstimateApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_oo_api(self):
        response = self.client.post(
            "/api/metrics/oo/calculate",
            data={
                "files": (
                    io.BytesIO(b"class User { private int score; public int getScore() { return score; } }"),
                    "User.java",
                ),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["summary"]["class_count"], 1)

    def test_estimate_api(self):
        response = self.client.post(
            "/api/metrics/estimate/calculate",
            json={"metric_type": "ucp", "metric_value": 10, "productivity": 20, "team_size": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["effort_hours"], 200)


if __name__ == "__main__":
    unittest.main()
