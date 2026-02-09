"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to clean state before each test"""
    # Clear participants from all activities
    for activity in activities.values():
        activity["participants"] = []
    yield
    # Clean up after test
    for activity in activities.values():
        activity["participants"] = []


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that expected activities are in the response"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Basketball", "Soccer", "Tennis", "Volleyball", "Painting"]
        for activity in expected_activities:
            assert activity in data


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        email = "test@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data["Basketball"]["participants"]

    def test_signup_duplicate_fails(self, client):
        """Test that duplicate signup for same activity fails"""
        email = "student@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for same activity"""
        response1 = client.post(
            "/activities/Basketball/signup?email=student1@mergington.edu"
        )
        response2 = client.post(
            "/activities/Basketball/signup?email=student2@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert len(participants) == 2
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        email = "student@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Then unregister
        response = client.post(f"/activities/Basketball/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "student@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Verify participant is there
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Verify participant is gone
        response = client.get("/activities")
        assert email not in response.json()["Basketball"]["participants"]

    def test_unregister_not_signed_up_fails(self, client):
        """Test that unregistering a non-participant fails"""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister for non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_unregister_cycle(self, client):
        """Test signup, unregister, and signup again cycle"""
        email = "student@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        response = client.get("/activities")
        assert email not in response.json()["Basketball"]["participants"]
        
        # Sign up again (should succeed since we unregistered)
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]


class TestRootRedirect:
    """Tests for root endpoint redirect"""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
