"""
Test suite for Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Should return all activities"""
        # Arrange
        # No setup needed - activities pre-populated by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_structure(self, client):
        """Should return activities with correct structure"""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        for field in expected_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Should successfully sign up a new student"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants
    
    def test_signup_activity_not_found(self, client):
        """Should return 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_student(self, client):
        """Should return 400 when student is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Should allow a student to sign up for multiple activities"""
        # Arrange
        email = "multiactivity@mergington.edu"
        activity_1 = "Chess Club"
        activity_2 = "Programming Class"
        
        # Act
        response_1 = client.post(
            f"/activities/{activity_1}/signup",
            params={"email": email}
        )
        response_2 = client.post(
            f"/activities/{activity_2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity_1]["participants"]
        assert email in data[activity_2]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Should successfully remove a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Verify participant exists before removal
        pre_activities = client.get("/activities").json()
        assert email in pre_activities[activity_name]["participants"]
        
        # Act - Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        post_activities = client.get("/activities").json()
        assert email not in post_activities[activity_name]["participants"]
    
    def test_remove_participant_activity_not_found(self, client):
        """Should return 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_participant_not_found(self, client):
        """Should return 404 when participant is not in activity"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notamember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_then_readd_participant(self, client):
        """Should allow re-signup after removal"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert remove_response.status_code == 200
        
        # Act - Re-add participant
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert signup_response.status_code == 200
        
        final_activities = client.get("/activities").json()
        assert email in final_activities[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirect(self, client):
        """Should redirect to /static/index.html"""
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location
