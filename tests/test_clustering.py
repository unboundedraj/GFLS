import io

import pandas as pd
import pytest

FEATURES = ["CO2 per capita", "GDP per capita", "Life expectancy", "Population"]


@pytest.fixture
def clustered(client, session):
    session_id, _ = session
    resp = client.post("/clustering/run", json={
        "session_id": session_id,
        "ref_year": 2023,
        "selected_features": FEATURES,
        "n_clusters": 3,
        "max_clusters": 6,
        "feature_weights": {"GDP per capita": 2.0},
    })
    assert resp.status_code == 200, resp.text
    return session_id, resp.json()


def test_clustering_splits_countries(clustered):
    _, body = clustered
    # 13 complete, 4 missing one metric, Argentina missing two
    assert body["countries_clustered"] == 13
    assert body["partial_countries"] == 4
    assert body["insufficient_countries"] == 1
    assert body["features_used"] == 4
    assert -1 <= body["silhouette_score"] <= 1
    assert {r["Cluster"] for r in body["clusters"]} == {0, 1, 2}
    assert len(body["elbow"]["k"]) == len(body["elbow"]["inertia"])


def test_clustering_rejects_unknown_features(client, session):
    session_id, _ = session
    resp = client.post("/clustering/run", json={
        "session_id": session_id,
        "selected_features": ["Not a metric"],
    })
    assert resp.status_code == 400


@pytest.mark.parametrize("k", [1, 3, 5, 50])
def test_knn_classifies_partial_countries(client, clustered, k):
    session_id, _ = clustered
    resp = client.post("/clustering/knn", json={"session_id": session_id, "n_neighbors": k})
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["classified"] == 4
    assert body["n_neighbors"] == min(k, 13)
    assert {r["country"] for r in body["knn_results"]} == {"Egypt", "Indonesia", "Kenya", "Nigeria"}
    assert all(0 < r["confidence"] <= 1 for r in body["knn_results"])


def test_knn_requires_clustering_first(client, session):
    session_id, _ = session
    resp = client.post("/clustering/knn", json={"session_id": session_id})
    assert resp.status_code == 404


def test_download_clustering_results(client, clustered):
    session_id, body = clustered
    resp = client.get(f"/clustering/download/{session_id}")
    assert resp.status_code == 200
    df = pd.read_csv(io.BytesIO(resp.content))
    assert len(df) == body["countries_clustered"]
    assert "Cluster" in df.columns


def test_diagnose(client, session):
    session_id, _ = session
    body = client.post(f"/clustering/diagnose/{session_id}").json()
    assert body["required_columns_present"] is True
    assert body["year_in_data"] is True
    assert set(body["available_features"]) == set(FEATURES)
