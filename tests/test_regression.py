import pytest

METHODS = [
    "linear", "polynomial", "ridge", "lasso", "logistic",
    "decision_tree", "random_forest", "svm", "neural_network",
]


def _predict(client, session_id, **overrides):
    payload = {
        "session_id": session_id,
        "country": "India",
        "metric": "GDP per capita",
        "target_year": 2026,
        "method": "linear",
        "hidden_layers": "10,10",
    }
    payload.update(overrides)
    return client.post("/regression/predict", json=payload)


@pytest.mark.parametrize("method", METHODS)
def test_predict_every_method(client, session, method):
    session_id, _ = session
    resp = _predict(client, session_id, method=method)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["method"] == method
    assert body["year"] == 2026
    assert isinstance(body["predicted_value"], float)


def test_linear_trend_extends_history(client, session):
    session_id, _ = session
    linear = _predict(client, session_id).json()["predicted_value"]
    # sample GDP per capita grows every year, so a 2026 forecast must be positive
    assert linear > 0


def test_needs_at_least_two_points(client, session):
    session_id, _ = session
    resp = _predict(client, session_id, country="Atlantis")
    assert resp.status_code == 400


def test_add_prediction_appends_row(client, session):
    session_id, uploaded = session
    resp = client.post("/regression/add-prediction", json={
        "session_id": session_id,
        "country": "India",
        "metric": "GDP per capita",
        "year": 2026,
        "value": 1234.5,
    })
    assert resp.status_code == 200
    assert resp.json() == {"status": "added", "rows": uploaded["rows"] + 1}
