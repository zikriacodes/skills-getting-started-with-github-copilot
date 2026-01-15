import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all():
    client = TestClient(app)
    response = client.get("/activities")

    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert isinstance(body["Chess Club"], dict)


def test_signup_adds_participant():
    client = TestClient(app)
    email = "newstudent@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_rejected():
    client = TestClient(app)
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    client = TestClient(app)

    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "person@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    client = TestClient(app)
    email = "daniel@mergington.edu"

    response = client.delete(
        f"/activities/Chess%20Club/participants/{email}"
    )

    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    client = TestClient(app)

    response = client.delete(
        "/activities/Chess%20Club/participants/nonexistent@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered for this activity"
