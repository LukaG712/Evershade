"""Cross-service mission integration tests.

These tests verify that the mission control system integrates correctly
with other Evershade services (Greenie API, Slinker, Shrewd) without
requiring external infrastructure like Junie CLI or cloud model providers.
"""

import pytest
import requests
from tests.conftest import SERVICES, API_KEYS


class TestMissionAPIHealth:
    """Verify the Mission API endpoints are accessible via Greenie."""

    def test_missions_list_endpoint(self):
        """GET /api/missions should return a valid response."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        resp = requests.get(f"{url}/api/missions", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "missions" in data
        assert isinstance(data["missions"], list)

    def test_missions_stats_endpoint(self):
        """GET /api/missions/stats should return valid stats."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        resp = requests.get(f"{url}/api/missions/stats", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_missions" in data
        assert "planning" in data
        assert "executing" in data
        assert "completed" in data
        assert "failed" in data

    def test_missions_analytics_endpoint(self):
        """GET /api/missions/analytics should return analytics data."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        resp = requests.get(f"{url}/api/missions/analytics", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_missions" in data
        assert "success_rate" in data


class TestMissionLifecycleViaAPI:
    """Test mission creation and lifecycle via the Greenie API."""

    def test_create_mission(self):
        """POST /api/missions should create a new mission."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        data = {
            "description": "Integration test mission",
            "target_repository": "test-repo",
            "autonomy_level": "restricted_autonomous",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200, f"Create mission failed: {resp.text}"
        result = resp.json()
        assert "id" in result
        assert result["description"] == "Integration test mission"
        assert result["status"] == "planning"

    def test_get_mission_detail(self):
        """GET /api/missions/{id} should return mission details."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission first
        data = {
            "description": "Detail test mission",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Get detail
        resp = requests.get(f"{url}/api/missions/{mission_id}", headers=headers, timeout=5)
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["id"] == mission_id
        assert detail["description"] == "Detail test mission"

    def test_cancel_mission(self):
        """POST /api/missions/{id}/cancel should cancel a mission."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Cancel test mission",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Cancel it
        resp = requests.post(f"{url}/api/missions/{mission_id}/cancel", headers=headers, timeout=5)
        assert resp.status_code == 200

        # Verify cancelled
        resp = requests.get(f"{url}/api/missions/{mission_id}", headers=headers, timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_mission_with_models(self):
        """Create a mission with model overrides."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        data = {
            "description": "Model override test",
            "target_repository": "test-repo",
            "orchestrator_model": "gpt-4o",
            "worker_model": "gpt-4o-mini",
            "validator_model": "claude-3-sonnet",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        result = resp.json()
        assert result["orchestrator_model"] == "gpt-4o"
        assert result["worker_model"] == "gpt-4o-mini"
        assert result["validator_model"] == "claude-3-sonnet"


class TestMissionPlanningViaAPI:
    """Test mission planning via the Greenie API."""

    def test_start_planning(self):
        """POST /api/missions/{id}/plan should start planning."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Add a health check endpoint to the API",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Start planning
        resp = requests.post(f"{url}/api/missions/{mission_id}/plan", headers=headers, timeout=15)
        assert resp.status_code == 200

        # Verify milestones were created (heuristic fallback)
        resp = requests.get(f"{url}/api/missions/{mission_id}", headers=headers, timeout=5)
        assert resp.status_code == 200
        detail = resp.json()
        assert len(detail.get("milestones", [])) > 0


class TestMissionValidationViaAPI:
    """Test mission validation via the Greenie API."""

    def test_add_validation_result(self):
        """POST /api/missions/{id}/validation should add a validation result."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Validation test",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Add validation result
        validation = {
            "severity": "minor",
            "file_path": "test.py",
            "line_number": 42,
            "explanation": "Missing type hint",
            "suggested_correction": "Add type hint to function parameter",
        }
        resp = requests.post(
            f"{url}/api/missions/{mission_id}/validation",
            json=validation,
            headers=headers,
            timeout=5,
        )
        assert resp.status_code == 200

        # Verify validation result
        resp = requests.get(f"{url}/api/missions/{mission_id}/validation", headers=headers, timeout=5)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0


class TestMissionAnalyticsViaAPI:
    """Test mission analytics endpoints."""

    def test_analytics_summary(self):
        """GET /api/missions/analytics should return analytics."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        resp = requests.get(f"{url}/api/missions/analytics", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_missions" in data
        assert "success_rate" in data
        assert "avg_total_duration_seconds" in data

    def test_validation_summary(self):
        """GET /api/missions/{id}/validation-summary should return validation summary."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Validation summary test",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Get validation summary
        resp = requests.get(
            f"{url}/api/missions/{mission_id}/validation-summary",
            headers=headers,
            timeout=5,
        )
        assert resp.status_code == 200
        summary = resp.json()
        assert "mission_id" in summary
        assert "total_findings" in summary
        assert "passed" in summary

    def test_mission_timeline(self):
        """GET /api/missions/{id}/timeline should return mission timeline."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Timeline test",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Get timeline
        resp = requests.get(f"{url}/api/missions/{mission_id}/timeline", headers=headers, timeout=5)
        assert resp.status_code == 200
        timeline = resp.json()
        assert "mission_id" in timeline
        assert "transitions" in timeline


class TestMissionLogsViaAPI:
    """Test mission log endpoints."""

    def test_get_mission_logs(self):
        """GET /api/missions/{id}/logs should return logs."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}

        # Create a mission
        data = {
            "description": "Log test",
            "target_repository": "test-repo",
        }
        resp = requests.post(f"{url}/api/missions", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200
        mission_id = resp.json()["id"]

        # Get logs
        resp = requests.get(f"{url}/api/missions/{mission_id}/logs", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "logs" in data
        assert isinstance(data["logs"], list)
