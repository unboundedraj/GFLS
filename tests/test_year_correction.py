import io

import pandas as pd
import pytest

INTERPOLATE = ["linear", "polynomial", "spline", "nearest_neighbour", "piecewise_constant", "logarithmic"]
EXTRAPOLATE = ["cagr", "linear_regression", "polynomial_regression", "moving_average_growth", "arima"]

# The sample data is missing six metric values for 2023
MISSING_2023 = 6


def _correct(client, session_id, fix_method, method):
    resp = client.post("/year-correction", json={
        "session_id": session_id,
        "ref_year": 2023,
        "fix_method": fix_method,
        "interp_method": method,
        "poly_order": 2,
        "ma_window": 3,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.mark.parametrize(
    "fix_method,method",
    [("Interpolate", m) for m in INTERPOLATE] + [("Extrapolate", m) for m in EXTRAPOLATE],
)
def test_fills_missing_values(client, session, fix_method, method):
    session_id, uploaded = session
    body = _correct(client, session_id, fix_method, method)

    assert body["original_missing"] == MISSING_2023
    assert body["final_missing"] == 0
    assert body["values_filled"] == MISSING_2023
    # only the filled cells are appended to the data
    assert body["shape"]["rows"] == uploaded["rows"] + MISSING_2023

    filled = body["filled_preview"]
    assert len(filled) == MISSING_2023
    assert all(r["year"] == 2023 and r["value"] is not None for r in filled)
    assert all(r["assumption"] == f"{fix_method} ({method})" for r in filled)


def test_does_not_duplicate_existing_rows(client, session):
    session_id, _ = session
    _correct(client, session_id, "Interpolate", "linear")

    df = pd.read_excel(io.BytesIO(client.get(f"/download/{session_id}").content))
    assert not df.duplicated(["country", "year", "metric"]).any()


def test_unknown_session(client):
    resp = client.post("/year-correction", json={"session_id": "does-not-exist"})
    assert resp.status_code == 404
