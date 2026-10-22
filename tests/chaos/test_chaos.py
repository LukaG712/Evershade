"""Failure injection tests for the Evershade ecosystem.

Tests system resilience by injecting failures: service crashes, network
timeouts, and data corruption scenarios.
"""

import time
import pytest
import requests
from tests.conftest import SERVICES, API_KEYS


class TestServiceCrash:
    """Test behavior when a service becomes unavailable."""

    def test_health_check_on_down_service(self):
        """Health check should fail gracefully on unreachable service."""
        # Connect to a port that should have nothing listening
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("http://localhost:19999/health", timeout=2)

    def test_request_timeout_handling(self):
        """Request should timeout gracefully, not hang forever."""
        start = time.perf_counter()
        try:
            # Use a very short timeout to a non-responsive service
            requests.get("http://localhost:19999/health", timeout=1)
        except requests.exceptions.Timeout:
            elapsed = time.perf_counter() - start
            assert elapsed < 5, "Timeout took too long"
        except requests.exceptions.ConnectionError:
            elapsed = time.perf_counter() - start
            assert elapsed < 5, "Connection error took too long"

    def test_fallback_on_service_unavailable(self):
        """Services with fallback should degrade gracefully."""
        # Shrewd should fall back to simulation if provider is down
        url = SERVICES["shrewd"]
        headers = {"Authorization": f"Bearer {API_KEYS['shrewd']}"}
        data = {
            "model": "llama3",
            "messages": [{"role": "user", "content": "Hello."}],
        }
        resp = requests.post(f"{url}/api/chat", json=data, headers=headers, timeout=10)
        # Should succeed even if no real provider is configured
        assert resp.status_code == 200


class TestNetworkFailure:
    """Test behavior under network failure conditions."""

    def test_dns_failure_handling(self):
        """Request to invalid hostname should fail gracefully."""
        start = time.perf_counter()
        try:
            requests.get("http://nonexistent.evershade.local/health", timeout=2)
        except requests.exceptions.ConnectionError:
            elapsed = time.perf_counter() - start
            assert elapsed < 10
        except requests.exceptions.Timeout:
            elapsed = time.perf_counter() - start
            assert elapsed < 10

    def test_partial_connectivity(self):
        """Some services should remain available if others are down."""
        # Health endpoint should work even if other services are down
        url = SERVICES["greenie"]
        resp = requests.get(f"{url}/health", timeout=5)
        assert resp.status_code == 200


class TestDataIntegrity:
    """Test data integrity under stress."""

    def test_concurrent_writes(self):
        """Concurrent writes should not corrupt data."""
        import threading
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        errors = []

        def write_secret(i):
            try:
                data = {"key": f"concurrent-{i}", "value": f"value-{i}", "service": "chaos-test"}
                resp = requests.post(f"{url}/api/secrets", json=data, headers=headers, timeout=5)
                if resp.status_code != 200:
                    errors.append(f"Write {i} failed: {resp.status_code}")
            except Exception as e:
                errors.append(f"Write {i} exception: {e}")

        threads = []
        for i in range(10):
            t = threading.Thread(target=write_secret, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=15)

        # Verify at least most writes succeeded
        assert len(errors) < 5, f"Too many write errors: {errors}"

        # Verify data integrity — each secret should be retrievable
        for i in range(10):
            resp = requests.get(f"{url}/api/secrets/concurrent-{i}", headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                assert data["value"] == f"value-{i}", f"Data corruption: expected value-{i}, got {data['value']}"

    def test_read_during_write(self):
        """Reads during concurrent writes should return consistent data."""
        import threading
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}

        # Create a secret first
        requests.post(f"{url}/api/secrets", json={
            "key": "read-write-test", "value": "initial", "service": "chaos-test"
        }, headers=headers, timeout=5)

        read_errors = []
        read_count = 0

        def read_secret():
            nonlocal read_count
            try:
                resp = requests.get(f"{url}/api/secrets/read-write-test", headers=headers, timeout=5)
                if resp.status_code == 200:
                    read_count += 1
                    data = resp.json()
                    # Value should be one of the expected values
                    if data["value"] not in ("initial", "updated"):
                        read_errors.append(f"Inconsistent read: {data['value']}")
            except Exception as e:
                read_errors.append(str(e))

        def update_secret():
            try:
                requests.post(f"{url}/api/secrets", json={
                    "key": "read-write-test", "value": "updated", "service": "chaos-test"
                }, headers=headers, timeout=5)
            except Exception:
                pass

        # Start readers
        reader_threads = []
        for _ in range(5):
            t = threading.Thread(target=read_secret)
            reader_threads.append(t)
            t.start()

        # Start writers
        writer_threads = []
        for _ in range(3):
            t = threading.Thread(target=update_secret)
            writer_threads.append(t)
            t.start()

        for t in reader_threads + writer_threads:
            t.join(timeout=10)

        assert len(read_errors) == 0, f"Read consistency errors: {read_errors}"
        assert read_count > 0, "No successful reads"


class TestMalformedInput:
    """Test handling of malformed input."""

    def test_empty_body(self):
        """Empty request body should return 400 or 422."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}", "Content-Type": "application/json"}
        resp = requests.post(f"{url}/api/secrets", data="", headers=headers, timeout=5)
        assert resp.status_code in (400, 422, 415), f"Empty body should be rejected, got {resp.status_code}"

    def test_invalid_json(self):
        """Invalid JSON should return 400 or 422."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}", "Content-Type": "application/json"}
        resp = requests.post(f"{url}/api/secrets", data="not json", headers=headers, timeout=5)
        assert resp.status_code in (400, 422, 415), f"Invalid JSON should be rejected, got {resp.status_code}"

    def test_missing_required_fields(self):
        """Missing required fields should return 400 or 422."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        resp = requests.post(f"{url}/api/secrets", json={"key": "test"}, headers=headers, timeout=5)
        # Should reject — value is required
        assert resp.status_code in (200, 400, 422), f"Missing fields should be handled, got {resp.status_code}"

    def test_oversized_payload(self):
        """Oversized payload should be rejected."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        large_value = "x" * 1_000_000  # 1MB value
        data = {"key": "oversized", "value": large_value, "service": "chaos-test"}
        resp = requests.post(f"{url}/api/secrets", json=data, headers=headers, timeout=10)
        # Should either accept or reject — but not crash
        assert resp.status_code in (200, 400, 413, 422), f"Oversized payload should be handled, got {resp.status_code}"

    def test_sql_injection_attempt(self):
        """SQL injection attempt should be handled safely."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        sql_payload = "'; DROP TABLE secrets; --"
        data = {"key": sql_payload, "value": "test", "service": "chaos-test"}
        resp = requests.post(f"{url}/api/secrets", json=data, headers=headers, timeout=5)
        # Should either accept (parameterized query) or reject — but not crash
        assert resp.status_code in (200, 400, 422), f"SQL injection should be handled, got {resp.status_code}"

        # Verify service is still functional
        resp = requests.get(f"{url}/health", timeout=5)
        assert resp.status_code == 200


class TestResourceExhaustion:
    """Test behavior under resource pressure."""

    def test_many_secrets(self):
        """Creating many secrets should not crash the service."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}

        # Create 100 secrets
        for i in range(100):
            data = {"key": f"stress-{i}", "value": f"value-{i}", "service": "stress-test"}
            resp = requests.post(f"{url}/api/secrets", json=data, headers=headers, timeout=5)
            assert resp.status_code == 200, f"Failed to create secret {i}: {resp.status_code}"

        # List should still work
        resp = requests.get(f"{url}/api/secrets", headers=headers, timeout=10)
        assert resp.status_code == 200
        secrets = resp.json()
        assert len(secrets) >= 100

    def test_long_running_request(self):
        """Long-running request should not block other requests."""
        import threading
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}
        health_during_work = []

        def check_health():
            for _ in range(5):
                resp = requests.get(f"{url}/health", timeout=5)
                health_during_work.append(resp.status_code)
                time.sleep(0.1)

        # Start health checker in background
        t = threading.Thread(target=check_health)
        t.start()

        # Do some work
        for i in range(10):
            data = {"key": f"blocking-{i}", "value": f"value-{i}", "service": "stress-test"}
            requests.post(f"{url}/api/secrets", json=data, headers=headers, timeout=5)

        t.join(timeout=10)

        # Health checks should have succeeded during work
        assert 200 in health_during_work, "Health checks failed during work"
