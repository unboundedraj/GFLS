import io

import pandas as pd
import pytest

from conftest import FORMAT1_MAPPING, SAMPLE_DIR

EXPECTED_METRICS = {"CO2 per capita", "GDP per capita", "Life expectancy", "Population"}

FORMATS = [
    ("format1_long", 1, FORMAT1_MAPPING, 641),
    ("format2_years_as_columns", 2, None, 641),
    ("format3_metrics_as_columns", 3, None, 641),
    ("format4_labelled_years", 4, None, 210),
]


@pytest.mark.parametrize("ext,file_type", [("csv", "CSV"), ("xlsx", "Excel")])
def test_preview_columns(client, ext, file_type):
    path = SAMPLE_DIR / f"format3_metrics_as_columns.{ext}"
    with open(path, "rb") as fh:
        resp = client.post(
            "/preview-columns",
            files={"file": (path.name, fh)},
            data={"file_type": file_type, "sheet_name": "Sheet1"},
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["columns"][:2] == ["Country", "Year"]
    assert len(body["preview"]) == 10
    assert body["total_rows"] == 162


@pytest.mark.parametrize("ext,file_type", [("csv", "CSV"), ("xlsx", "Excel")])
@pytest.mark.parametrize("stem,format_num,mapping,rows", FORMATS)
def test_upload_every_format(upload, stem, format_num, mapping, rows, ext, file_type):
    _, body = upload(f"{stem}.{ext}", format_num, file_type, mapping)

    assert body["rows"] == rows
    assert body["columns"][:4] == ["country", "year", "metric", "value"]
    assert len(body["countries"]) == 18
    assert set(body["metrics"]) == EXPECTED_METRICS
    assert set(body["pivot_features"]) == EXPECTED_METRICS
    assert 2023 in body["available_years"]


def test_invalid_format_is_rejected(client):
    path = SAMPLE_DIR / "format3_metrics_as_columns.csv"
    with open(path, "rb") as fh:
        resp = client.post(
            "/upload",
            files={"file": (path.name, fh)},
            data={"file_type": "CSV", "format_num": "9", "session_id": "bad-format"},
        )
    assert resp.status_code == 400


def test_download_formatted_data(client, session):
    session_id, body = session
    resp = client.get(f"/download/{session_id}", params={"filename": "out.xlsx"})
    assert resp.status_code == 200
    assert 'filename="out.xlsx"' in resp.headers["content-disposition"]
    assert len(pd.read_excel(io.BytesIO(resp.content))) == body["rows"]


def test_download_unknown_session(client):
    assert client.get("/download/does-not-exist").status_code == 404
