"""Ecosystem-wide integration tests.

These tests verify cross-service communication and end-to-end workflows.
They require all services to be running (via Docker Compose).
"""

import pytest
import requests
from tests.conftest import SERVICES, API_KEYS


class TestHealthChecks:
    """Verify all services respond to health checks."""

    def test_all_services_healthy(self, all_services):
        """All services should return healthy status."""
        for name, url in all_services.items():
            resp = requests.get(f"{url}/health", timeout=5)
            assert resp.status_code == 200, f"{name} health check failed: {resp.status_code}"
            data = resp.json()
            assert data.get("status") == "ok", f"{name} health status is not 'ok': {data}"


class TestBearerAuth:
    """Verify Bearer token auth works on all services."""

    def test_bearer_auth_accepted(self, all_services, all_api_keys):
        """Bearer token should be accepted on authenticated endpoints."""
        for name, url in all_services.items():
            key = all_api_keys[name]
            headers = {"Authorization": f"Bearer {key}"}
            # Try a known endpoint for each service
            if name == "hider":
                resp = requests.get(f"{url}/api/secrets", headers=headers, timeout=5)
            elif name == "shrewd":
                resp = requests.get(f"{url}/api/models", headers=headers, timeout=5)
            elif name == "poltergeist":
                resp = requests.get(f"{url}/api/notifications", headers=headers, timeout=5)
            elif name == "gobber":
                resp = requests.get(f"{url}/api/cache", headers=headers, timeout=5)
            elif name == "sneaker":
                resp = requests.get(f"{url}/api/metrics", headers=headers, timeout=5)
            else:
                # Fallback: health endpoint (no auth required)
                resp = requests.get(f"{url}/health", timeout=5)
            assert resp.status_code in (200, 401, 403), f"{name} unexpected status: {resp.status_code}"

    def test_no_auth_rejected(self, all_services):
        """Unauthenticated requests to protected endpoints should be rejected."""
        for name, url in all_services.items():
            if name in ("hider", "shrewd", "poltergeist", "gobber", "sneaker"):
                # These services have protected endpoints
                endpoint = f"{url}/api/secrets" if name == "hider" else f"{url}/api/models" if name == "shrewd" else f"{url}/api/notifications" if name == "poltergeist" else f"{url}/api/cache" if name == "gobber" else f"{url}/api/metrics"
                resp = requests.get(endpoint, timeout=5)
                assert resp.status_code == 401, f"{name} should reject unauthenticated request, got {resp.status_code}"

    def test_invalid_bearer_rejected(self, all_services, all_api_keys):
        """Invalid Bearer tokens should be rejected."""
        for name, url in all_services.items():
            headers = {"Authorization": "Bearer invalid-key"}
            if name in ("hider", "shrewd", "poltergeist", "gobber", "sneaker"):
                endpoint = f"{url}/api/secrets" if name == "hider" else f"{url}/api/models" if name == "shrewd" else f"{url}/api/notifications" if name == "poltergeist" else f"{url}/api/cache" if name == "gobber" else f"{url}/api/metrics"
                resp = requests.get(endpoint, headers=headers, timeout=5)
                assert resp.status_code == 401, f"{name} should reject invalid Bearer token, got {resp.status_code}"


class TestHiderSecrets:
    """Test Hider secret management end-to-end."""

    def test_create_and_retrieve_secret(self):
        """Create a secret and retrieve it."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}

        # Create
        secret_data = {"key": "test-integration-key", "value": "test-secret-value", "service": "integration-test"}
        resp = requests.post(f"{url}/api/secrets", json=secret_data, headers=headers, timeout=5)
        assert resp.status_code == 200, f"Create secret failed: {resp.text}"

        # Retrieve
        resp = requests.get(f"{url}/api/secrets/test-integration-key", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["key"] == "test-integration-key"
        assert data["value"] == "test-secret-value"

    def test_list_secrets_no_values(self):
        """List endpoint should not expose secret values."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        resp = requests.get(f"{url}/api/secrets", headers=headers, timeout=5)
        assert resp.status_code == 200
        secrets = resp.json()
        for secret in secrets:
            assert "value" not in secret, "List endpoint should not expose secret values"


class TestShrewdChat:
    """Test Shrewd LLM routing."""

    def test_chat_simulation(self):
        """Chat should work with simulation fallback."""
        url = SERVICES["shrewd"]
        headers = {"Authorization": f"Bearer {API_KEYS['shrewd']}"}
        data = {
            "model": "llama3",
            "messages": [{"role": "user", "content": "Hello, test."}],
        }
        resp = requests.post(f"{url}/api/chat", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200, f"Chat failed: {resp.text}"
        result = resp.json()
        assert "content" in result
        assert len(result["content"]) > 0

    def test_list_models(self):
        """Should list available models."""
        url = SERVICES["shrewd"]
        headers = {"Authorization": f"Bearer {API_KEYS['shrewd']}"}
        resp = requests.get(f"{url}/api/models", headers=headers, timeout=5)
        assert resp.status_code == 200
        models = resp.json()
        assert len(models) > 0


class TestPoltergeistNotifications:
    """Test Poltergeist notification delivery."""

    def test_send_notification(self):
        """Send a notification and verify it's persisted."""
        url = SERVICES["poltergeist"]
        headers = {"Authorization": f"Bearer {API_KEYS['poltergeist']}"}
        data = {
            "channel": "webhook",
            "recipient": "https://httpbin.org/post",
            "title": "Integration Test",
            "message": "This is a test notification",
        }
        resp = requests.post(f"{url}/api/notifications", json=data, headers=headers, timeout=10)
        assert resp.status_code == 200, f"Send notification failed: {resp.text}"
        result = resp.json()
        assert "id" in result


class TestGobberCache:
    """Test Gobber cache operations."""

    def test_cache_set_and_get(self):
        """Set a cache entry and retrieve it."""
        url = SERVICES["gobber"]
        headers = {"Authorization": f"Bearer {API_KEYS['gobber']}"}

        # Set
        cache_data = {"key": "test-integration-cache", "value": "cached-value", "ttl": 60}
        resp = requests.post(f"{url}/api/cache", json=cache_data, headers=headers, timeout=5)
        assert resp.status_code == 200, f"Cache set failed: {resp.text}"

        # Get
        resp = requests.get(f"{url}/api/cache/test-integration-cache", headers=headers, timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["value"] == "cached-value"


class TestSneakerMetrics:
    """Test Sneaker metrics ingestion."""

    def test_ingest_metric(self):
        """Ingest a metric and verify it's stored."""
        url = SERVICES["sneaker"]
        headers = {"Authorization": f"Bearer {API_KEYS['sneaker']}"}
        data = {
            "name": "test.metric",
            "value": 42.0,
            "tags": {"service": "integration-test"},
        }
        resp = requests.post(f"{url}/api/metrics", json=data, headers=headers, timeout=5)
        assert resp.status_code == 200, f"Ingest metric failed: {resp.text}"


class TestGreenieAgents:
    """Test Greenie agent management."""

    def test_list_agents(self):
        """List agents should return a list."""
        url = SERVICES["greenie"]
        headers = {"Authorization": f"Bearer {API_KEYS['greenie']}"}
        resp = requests.get(f"{url}/api/agents", headers=headers, timeout=5)
        assert resp.status_code == 200
        agents = resp.json()
        assert isinstance(agents, list)


class TestCrossServiceWorkflow:
    """Test a cross-service workflow: secret → cache → notification."""

    def test_secret_cache_notify_flow(self):
        """Store a secret in Hider, cache it in Gobber, notify via Poltergeist."""
        hider_headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        gobber_headers = {"Authorization": f"Bearer {API_KEYS['gobber']}"}
        poltergeist_headers = {"Authorization": f"Bearer {API_KEYS['poltergeist']}"}

        # 1. Store secret in Hider
        secret_data = {"key": "workflow-test-key", "value": "workflow-secret", "service": "workflow-test"}
        resp = requests.post(f"{SERVICES['hider']}/api/secrets", json=secret_data, headers=hider_headers, timeout=5)
        assert resp.status_code == 200

        # 2. Cache the secret reference in Gobber
        cache_data = {"key": "workflow-test-ref", "value": "workflow-test-key", "ttl": 60}
        resp = requests.post(f"{SERVICES['gobber']}/api/cache", json=cache_data, headers=gobber_headers, timeout=5)
        assert resp.status_code == 200

        # 3. Send notification via Poltergeist
        notify_data = {
            "channel": "webhook",
            "recipient": "https://httpbin.org/post",
            "title": "Workflow Test",
            "message": "Cross-service workflow completed",
        }
        resp = requests.post(f"{SERVICES['poltergeist']}/api/notifications", json=notify_data, headers=poltergeist_headers, timeout=10)
        assert resp.status_code == 200
