import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participant lists to a known state before each test."""
    original = {
        name: list(data["participants"])
        for name, data in activities.items()
    }
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_has_required_fields(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


def test_signup_success(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant(client):
    # Arrange
    email = "addedstudent@mergington.edu"

    # Act
    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert activities_response.status_code == 200
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_unknown_activity(client):
    # Arrange
    email = "x@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_full(client):
    # Arrange
    activity = activities["Gym Class"]
    while len(activity["participants"]) < activity["max_participants"]:
        index = len(activity["participants"])
        activity["participants"].append(f"filler{index}@mergington.edu")

    # Act
    response = client.post(
        "/activities/Gym Class/signup",
        params={"email": "overflow@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_success(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant(client):
    # Arrange
    email = "daniel@mergington.edu"

    # Act
    unregister_response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert activities_response.status_code == 200
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_unknown_activity(client):
    # Arrange
    email = "x@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]
