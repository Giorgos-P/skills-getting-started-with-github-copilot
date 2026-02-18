from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure not already in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_and_full():
    activity = "Basketball Team"
    # Prepare
    activities[activity]["participants"] = []
    max_p = activities[activity]["max_participants"]

    # Fill the activity
    for i in range(max_p):
        addr = f"user{i}@example.com"
        resp = client.post(f"/activities/{activity}/signup?email={addr}")
        assert resp.status_code == 200

    # Try to sign up one more
    resp = client.post(f"/activities/{activity}/signup?email=overflow@example.com")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Activity is full"

    # Try duplicate signup
    existing = f"user0@example.com"
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is already signed up for this activity"

    # Cleanup
    activities[activity]["participants"] = []
