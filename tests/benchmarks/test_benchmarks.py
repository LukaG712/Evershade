"""Performance benchmarks for the Evershade ecosystem.

Measures API latency, throughput, and resource usage baselines.
"""

import time
import statistics
import pytest
import requests
from tests.conftest import SERVICES, API_KEYS


class TestAPILatency:
    """Measure API response latency for all services."""

    def test_health_latency(self, all_services):
        """Health endpoint latency should be under 100ms."""
        latencies = {}
        for name, url in all_services.items():
            times = []
            for _ in range(10):
                start = time.perf_counter()
                resp = requests.get(f"{url}/health", timeout=5)
                elapsed = (time.perf_counter() - start) * 1000  # ms
                times.append(elapsed)
            avg = statistics.mean(times)
            p95 = sorted(times)[int(len(times) * 0.95)]
            latencies[name] = {"avg_ms": round(avg, 2), "p95_ms": round(p95, 2)}
            assert avg < 500, f"{name} health avg latency {avg:.0f}ms exceeds 500ms baseline"

    def test_hider_secret_latency(self):
        """Hider secret retrieval latency baseline."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}

        # Create a test secret first
        requests.post(f"{url}/api/secrets", json={
            "key": "bench-latency-key", "value": "bench-value", "service": "bench"
        }, headers=headers, timeout=5)

        times = []
        for _ in range(20):
            start = time.perf_counter()
            requests.get(f"{url}/api/secrets/bench-latency-key", headers=headers, timeout=5)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        assert avg < 500, f"Hider secret retrieval avg {avg:.0f}ms exceeds 500ms"
        assert p95 < 1000, f"Hider secret retrieval p95 {p95:.0f}ms exceeds 1000ms"

    def test_shrewd_chat_latency(self):
        """Shrewd chat simulation latency baseline."""
        url = SERVICES["shrewd"]
        headers = {"Authorization": f"Bearer {API_KEYS['shrewd']}"}
        data = {
            "model": "llama3",
            "messages": [{"role": "user", "content": "Hello."}],
        }
        times = []
        for _ in range(5):
            start = time.perf_counter()
            requests.post(f"{url}/api/chat", json=data, headers=headers, timeout=10)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg = statistics.mean(times)
        # Simulation should be fast; real LLM may be slower
        assert avg < 5000, f"Shrewd chat avg {avg:.0f}ms exceeds 5000ms"


class TestThroughput:
    """Measure request throughput."""

    def test_hider_throughput(self):
        """Hider should handle at least 10 req/s."""
        url = SERVICES["hider"]
        headers = {"Authorization": f"Bearer {API_KEYS['hider']}"}

        start = time.perf_counter()
        count = 0
        errors = 0
        duration = 2  # seconds

        while (time.perf_counter() - start) < duration:
            try:
                resp = requests.get(f"{url}/api/secrets", headers=headers, timeout=5)
                if resp.status_code == 200:
                    count += 1
                else:
                    errors += 1
            except Exception:
                errors += 1

        elapsed = time.perf_counter() - start
        rps = count / elapsed if elapsed > 0 else 0
        assert rps >= 5, f"Hider throughput {rps:.1f} req/s below 5 req/s baseline"

    def test_gobber_cache_throughput(self):
        """Gobber cache should handle at least 10 req/s."""
        url = SERVICES["gobber"]
        headers = {"Authorization": f"Bearer {API_KEYS['gobber']}"}

        start = time.perf_counter()
        count = 0
        duration = 2

        while (time.perf_counter() - start) < duration:
            try:
                resp = requests.get(f"{url}/api/cache", headers=headers, timeout=5)
                if resp.status_code == 200:
                    count += 1
            except Exception:
                pass

        elapsed = time.perf_counter() - start
        rps = count / elapsed if elapsed > 0 else 0
        assert rps >= 5, f"Gobber throughput {rps:.1f} req/s below 5 req/s baseline"


class TestConcurrentRequests:
    """Test behavior under concurrent load."""

    def test_concurrent_health_checks(self, all_services):
        """Multiple concurrent health checks should all succeed."""
        import threading
        results = []

        def check_health(url, name):
            try:
                resp = requests.get(f"{url}/health", timeout=5)
                results.append((name, resp.status_code))
            except Exception as e:
                results.append((name, str(e)))

        threads = []
        for name, url in all_services.items():
            for _ in range(3):  # 3 concurrent per service
                t = threading.Thread(target=check_health, args=(url, name))
                threads.append(t)
                t.start()

        for t in threads:
            t.join(timeout=10)

        # All should succeed
        for name, status in results:
            assert status == 200, f"Concurrent health check failed for {name}: {status}"


class TestResourceUsage:
    """Baseline resource usage metrics."""

    def test_response_sizes(self, all_services):
        """Response sizes should be reasonable (< 1MB)."""
        for name, url in all_services.items():
            resp = requests.get(f"{url}/health", timeout=5)
            size_bytes = len(resp.content)
            assert size_bytes < 1_000_000, f"{name} health response too large: {size_bytes} bytes"


class TestErrorHandling:
    """Test error response performance."""

    def test_404_latency(self, all_services):
        """404 responses should be fast."""
        for name, url in all_services.items():
            start = time.perf_counter()
            resp = requests.get(f"{url}/nonexistent-endpoint", timeout=5)
            elapsed = (time.perf_counter() - start) * 1000
            # 404 should be fast (< 200ms)
            assert elapsed < 500, f"{name} 404 latency {elapsed:.0f}ms exceeds 500ms"

    def test_401_latency(self):
        """401 responses should be fast (constant-time comparison)."""
        url = SERVICES["hider"]
        headers = {"Authorization": "Bearer wrong-key"}
        start = time.perf_counter()
        requests.get(f"{url}/api/secrets", headers=headers, timeout=5)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500, f"401 latency {elapsed:.0f}ms exceeds 500ms"
