import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "sara@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")
    encoded_email = urllib.parse.quote(email, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")
    encoded_email = urllib.parse.quote(email, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_from_activity_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")
    encoded_email = urllib.parse.quote(email, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/unregister?email={encoded_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_error_for_non_registered_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity_name = urllib.parse.quote(activity_name, safe="")
    encoded_email = urllib.parse.quote(email, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/unregister?email={encoded_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
