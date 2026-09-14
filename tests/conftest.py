import json
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api import app  # noqa: E402

SAMPLE_DIR = ROOT / "sample_data"

FORMAT1_MAPPING = {
    "Nation": "country", "Yr": "year", "Indicator": "metric",
    "Amount": "value", "Data Source": "source", "Notes": "assumption",
}


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def upload(client):
    """Upload a sample file into a fresh session and return (session_id, response_json)."""

    def _upload(name, format_num, file_type="CSV", column_mapping=None):
        session_id = uuid.uuid4().hex[:12]
        data = {
            "file_type": file_type,
            "sheet_name": "Sheet1",
            "format_num": str(format_num),
            "session_id": session_id,
        }
        if column_mapping:
            data["column_mapping"] = json.dumps(column_mapping)
        path = SAMPLE_DIR / name
        with open(path, "rb") as fh:
            resp = client.post("/upload", files={"file": (path.name, fh)}, data=data)
        assert resp.status_code == 200, resp.text
        return session_id, resp.json()

    return _upload


@pytest.fixture
def session(upload):
    """A session holding the format-3 sample, the most common layout."""
    return upload("format3_metrics_as_columns.csv", 3)
