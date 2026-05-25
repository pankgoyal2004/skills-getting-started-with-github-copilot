import copy

import pytest
from fastapi.testclient import TestClient

from src import app as application_module

client = TestClient(application_module.app)
initial_activities = copy.deepcopy(application_module.activities)


def reset_activities():
    application_module.activities.clear()
    application_module.activities.update(copy.deepcopy(initial_activities))


@pytest.fixture(autouse=True)
def restore_activities():
    reset_activities()
    yield
    reset_activities()


def test_get_activities_returns_activity_data():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "test.student@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    email = "duplicate.student@mergington.edu"
    activity_name = "Programming Class"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_unsubscribes_student():
    # Arrange
    email = "remove.student@mergington.edu"
    activity_name = "Gym Class"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    email = "missing.student@mergington.edu"
    activity_name = "Drama Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
