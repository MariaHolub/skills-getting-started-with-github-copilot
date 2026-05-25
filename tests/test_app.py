"""
Tests for the Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test state and prepare fixtures
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Test that GET /activities returns all available activities
        
        AAA Pattern:
        - Arrange: Activities are initialized via fresh_activities fixture
        - Act: Make GET request to /activities
        - Assert: Status code is 200 and response contains all activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9  # Should have all 9 activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_response_structure(self, client, fresh_activities):
        """
        Test that GET /activities returns activities with correct structure
        
        AAA Pattern:
        - Arrange: Activities are initialized via fresh_activities fixture
        - Act: Make GET request to /activities
        - Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, fresh_activities):
        """
        Test successful signup for an activity
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Make POST request to signup with valid activity and email
        - Assert: Status code is 200 and response confirms signup
        """
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
        assert f"Signed up {email}" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, fresh_activities):
        """
        Test that signup actually adds the participant to the activity's participant list
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Sign up new student and retrieve activities
        - Assert: Participant appears in the activity's participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client, fresh_activities):
        """
        Test that signup fails when student is already registered
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Sign up same student twice
        - Assert: Second signup returns 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Test that signup fails when activity does not exist
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Try to signup for non-existent activity
        - Assert: Status code is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_does_not_enforce_max_participants(self, client, fresh_activities):
        """
        Test that signup does not enforce max_participants limit (current behavior)
        
        AAA Pattern:
        - Arrange: Fresh activities fixture, sign up students until exceeding max
        - Act: Sign up more students than max_participants allows
        - Assert: All signups succeed (documenting current behavior)
        """
        # Arrange
        activity_name = "Tennis Club"
        max_participants = fresh_activities[activity_name]["max_participants"]
        current_count = len(fresh_activities[activity_name]["participants"])
        
        # Act - Sign up enough students to exceed max
        for i in range(max_participants + 5):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            # Assert - Should always succeed (documenting current behavior)
            assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, fresh_activities):
        """
        Test successful unregister from an activity
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up with participants
        - Act: Make DELETE request to unregister a participant
        - Assert: Status code is 200 and response confirms unregister
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert f"Unregistered {email}" in response.json()["message"]

    def test_unregister_removes_participant(self, client, fresh_activities):
        """
        Test that unregister actually removes the participant from the activity
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Unregister a participant and retrieve activities
        - Assert: Participant no longer appears in the activity's participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_student_returns_404(self, client, fresh_activities):
        """
        Test that unregister fails when student is not registered
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Try to unregister a student not registered for activity
        - Assert: Status code is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Test that unregister fails when activity does not exist
        
        AAA Pattern:
        - Arrange: Fresh activities fixture is set up
        - Act: Try to unregister from non-existent activity
        - Assert: Status code is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
