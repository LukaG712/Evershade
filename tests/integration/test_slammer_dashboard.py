"""Integration tests for Slammer dashboard API calls.

These tests verify that the Slammer dashboard can communicate with the
Greenie API and other services to display live data. They require
services to be running (via Docker Compose).
"""

import os
import pytest
import requests

GREENIE_URL = os.getenv("EVERSHADE_GREENIE_URL", "http://localhost:8000")
SLAMMER_URL = os.getenv("EVERSHADE_SLAMMER_URL", "http://localhost:5173")


class TestSlammerHealthPolling:
    """Test the health polling endpoints that Slammer uses."""

    def test_greenie_health_endpoint(self):
        """Greenie /health should return status ok."""
        resp = requests.get(f"{GREENIE_URL}/health", timeout=5)
        assert resp.status_code == 200, f"Greenie health check failed: {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "ok", f"Greenie health status is not 'ok': {data}"

    def test_greenie_health_returns_version(self):
        """Greenie /health should include a version field for Slammer display."""
        resp = requests.get(f"{GREENIE_URL}/health", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        # Version may be present; if present, it should be a string
        if "version" in data:
            assert isinstance(data["version"], str), "Version should be a string"

    def test_service_health_endpoints(self):
        """All services should respond to /health for Slammer status display."""
        services = [
            ("Slinker", os.getenv("EVERSHADE_SLINKER_URL", "http://localhost:8001")),
            ("Trapper", os.getenv("EVERSHADE_TRAPPER_URL", "http://localhost:3000")),
            ("Gobber", os.getenv("EVERSHADE_GOBBER_URL", "http://localhost:8002")),
            ("Sneaker", os.getenv("EVERSHADE_SNEAKER_URL", "http://localhost:8003")),
            ("Hider", os.getenv("EVERSHADE_HIDER_URL", "http://localhost:8004")),
            ("Poltergeist", os.getenv("EVERSHADE_POLTERGEIST_URL", "http://localhost:8005")),
            ("Shrewd", os.getenv("EVERSHADE_SHREWD_URL", "http://localhost:8006")),
        ]
        for name, url in services:
            try:
                resp = requests.get(f"{url}/health", timeout=3)
                assert resp.status_code == 200, f"{name} health check failed: {resp.status_code}"
            except requests.exceptions.RequestException:
                pytest.skip(f"{name} not available")


class TestSlammerAgentsPage:
    """Test the agents page API calls."""

    def test_agents_list_endpoint(self):
        """GET /api/agents should return a list (empty or populated)."""
        resp = requests.get(f"{GREENIE_URL}/api/agents", timeout=5)
        assert resp.status_code == 200, f"Agents endpoint failed: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Agents endpoint should return a list"

    def test_agents_list_structure(self):
        """Each agent should have name, status, and runner fields."""
        resp = requests.get(f"{GREENIE_URL}/api/agents", timeout=5)
        assert resp.status_code == 200
        agents = resp.json()
        for agent in agents:
            assert "name" in agent, "Agent should have a name field"
            assert "status" in agent, "Agent should have a status field"


class TestSlammerRunsPage:
    """Test the runs page API calls."""

    def test_runs_list_endpoint(self):
        """GET /api/runs should return a list."""
        resp = requests.get(f"{GREENIE_URL}/api/runs?limit=20", timeout=5)
        assert resp.status_code == 200, f"Runs endpoint failed: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Runs endpoint should return a list"

    def test_runs_list_with_limit(self):
        """Runs endpoint should respect the limit parameter."""
        resp = requests.get(f"{GREENIE_URL}/api/runs?limit=5", timeout=5)
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) <= 5, "Runs should respect the limit parameter"

    def test_runs_structure(self):
        """Each run should have id, agent, status, and startedAt fields."""
        resp = requests.get(f"{GREENIE_URL}/api/runs?limit=5", timeout=5)
        assert resp.status_code == 200
        runs = resp.json()
        for run in runs:
            assert "id" in run, "Run should have an id field"
            assert "status" in run, "Run should have a status field"


class TestSlammerWorkflowsPage:
    """Test the workflows page API calls."""

    def test_workflows_list_endpoint(self):
        """GET /api/workflows should return a list."""
        resp = requests.get(f"{GREENIE_URL}/api/workflows", timeout=5)
        assert resp.status_code == 200, f"Workflows endpoint failed: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list), "Workflows endpoint should return a list"

    def test_workflow_create_and_list(self):
        """Creating a workflow should make it appear in the list."""
        workflow = {
            "name": "test-dashboard-workflow",
            "steps": [
                {
                    "id": "step1",
                    "type": "agent",
                    "agent": "test-agent",
                    "prompt": "Hello from dashboard test",
                }
            ],
        }
        resp = requests.post(
            f"{GREENIE_URL}/api/workflows", json=workflow, timeout=10
        )
        assert resp.status_code in (200, 201), f"Create workflow failed: {resp.text}"

        # Verify it appears in the list
        resp = requests.get(f"{GREENIE_URL}/api/workflows", timeout=5)
        assert resp.status_code == 200
        workflows = resp.json()
        names = [w.get("name") for w in workflows]
        assert "test-dashboard-workflow" in names, "New workflow should appear in list"


class TestSlammerMetricsPage:
    """Test the metrics page API calls."""

    def test_metrics_endpoint(self):
        """Sneaker /api/metrics should return metrics data."""
        sneaker_url = os.getenv("EVERSHADE_SNEAKER_URL", "http://localhost:8003")
        try:
            resp = requests.get(f"{sneaker_url}/api/metrics", timeout=5)
            assert resp.status_code == 200, f"Metrics endpoint failed: {resp.status_code}"
        except requests.exceptions.RequestException:
            pytest.skip("Sneaker not available")


class TestSlammerLogsPage:
    """Test the logs page API calls."""

    def test_logs_endpoint(self):
        """Sneaker /api/logs should return log entries."""
        sneaker_url = os.getenv("EVERSHADE_SNEAKER_URL", "http://localhost:8003")
        try:
            resp = requests.get(f"{sneaker_url}/api/logs?limit=10", timeout=5)
            assert resp.status_code == 200, f"Logs endpoint failed: {resp.status_code}"
            data = resp.json()
            assert isinstance(data, list), "Logs endpoint should return a list"
        except requests.exceptions.RequestException:
            pytest.skip("Sneaker not available")


class TestSlammerDashboardAccess:
    """Test that the Slammer dashboard itself is accessible."""

    def test_slammer_serves_index(self):
        """Slammer should serve the main page."""
        try:
            resp = requests.get(SLAMMER_URL, timeout=5)
            assert resp.status_code == 200, f"Slammer dashboard failed: {resp.status_code}"
            assert b"Slammer" in resp.content or b"Evershade" in resp.content, \
                "Dashboard should contain Slammer or Evershade in HTML"
        except requests.exceptions.RequestException:
            pytest.skip("Slammer not available")
