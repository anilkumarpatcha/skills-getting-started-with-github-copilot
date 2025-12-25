import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get initial activities
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data["Chess Club"]["participants"])

    # Sign up a new student
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = len(updated_data["Chess Club"]["participants"])
    assert updated_participants == initial_participants + 1
    assert "test@example.com" in updated_data["Chess Club"]["participants"]


def test_signup_duplicate():
    """Test signing up for the same activity twice"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a nonexistent activity"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    client.post("/activities/Programming%20Class/signup?email=unregister@example.com")

    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data["Programming Class"]["participants"])

    # Unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]
    assert "Programming Class" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = len(updated_data["Programming Class"]["participants"])
    assert updated_participants == initial_participants - 1
    assert "unregister@example.com" not in updated_data["Programming Class"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering when not signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity():
    """Test unregistering from a nonexistent activity"""
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI's RedirectResponse should work, but in test client it might return the redirect
    # Let's check if it redirects or serves the content
    assert response.status_code in [200, 307]  # 307 is temporary redirect