# Evershade Testing Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-23

---

## 1. Test Structure

Evershade has a comprehensive test strategy covering multiple levels:

```
Test Pyramid
─────────────────────────────────
         /    E2E     \          ← Full system tests
        /   Integration \        ← Cross-service tests
       /      Unit Tests \       ← Individual component tests
      ─────────────────────
```

Each service maintains its own test suite in its separate repository:

| Service | Framework | Test Location | Run Command |
|---------|-----------|---------------|-------------|
| Greenie | pytest | `Greenie/tests/` | `cd Greenie && pytest` |
| Slinker | pytest | `Slinker/tests/` | `cd Slinker && pytest` |
| Trapper | Jest | `Trapper/tests/` | `cd Trapper && npm test` |
| Gobber | pytest | `Gobber/tests/` | `cd Gobber && pytest` |
| Sneaker | pytest | `Sneaker/tests/` | `cd Sneaker && pytest` |
| Hider | pytest | `Hider/tests/` | `cd Hider && pytest` |
| Poltergeist | pytest | `Poltergeist/tests/` | `cd Poltergeist && pytest` |
| Shrewd | pytest | `Shrewd/tests/` | `cd Shrewd && pytest` |

> **Note:** Service directories are cloned by the install script. Run `./install.sh` (or `.\install.ps1`) first to obtain the service code.

---

## 2. Running Tests

### Individual Service

```bash
# Install services first
./install.sh --profile standard

# Python services
cd Greenie
pip install -e ".[test]"
pytest -v

# TypeScript services
cd Trapper
npm install
npm test
```

### In Docker

```bash
# Test a specific service
docker compose run --rm Greenie pytest -v

# Test all Python services
for svc in Greenie Slinker Gobber Sneaker Hider Poltergeist Shrewd; do
  docker compose run --rm $svc pytest -v
done

# Test Trapper
docker compose run --rm Trapper-api npm test
```

---

## 3. Per-Service CI

Each service has its own GitHub Actions workflow in its repository:
- Lint and format check
- Type checking (where applicable)
- Unit tests
- Build verification

---

## 4. Writing Tests

### Python (pytest)

```python
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### TypeScript (Jest)

```typescript
test('health endpoint returns ok', async () => {
  const response = await request(app).get('/health');
  expect(response.status).toBe(200);
  expect(response.body.status).toBe('ok');
});
```

---

## 5. Test Data

- Use deterministic test fixtures, not random data
- Fake LLM providers for routine CI (no API costs)
- Real services for integration tests
- Clean up test data after each test

---

## 6. Test Categories Explained

### Unit Tests

Test individual functions and classes in isolation. Fast, no services required.

```python
# Example: Test a utility function
def test_generate_api_key():
    key = generate_api_key()
    assert len(key) == 64
    assert all(c in '0123456789abcdef' for c in key)
```

### Integration Tests

Test cross-service communication. Requires running services.

```python
# Example: Test Greenie → Slinker communication
async def test_create_task():
    response = await client.post("/api/tasks", json={"prompt": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
```

### Security Tests

Test for common vulnerabilities:
- **Prompt injection:** Verify untrusted content is treated as data
- **SSRF:** Verify private IP blocking in Trapper
- **Auth bypass:** Verify all endpoints require authentication
- **Secret leakage:** Verify secrets are redacted from logs

### Performance Benchmarks

Measure latency, throughput, and resource usage:
- **API latency:** p50, p95, p99 response times
- **Throughput:** Requests per second under load
- **Concurrency:** Behavior under concurrent access
- **Memory:** Peak memory usage per service

### Chaos Tests

Test resilience under failure conditions:
- **Service crash:** Verify graceful degradation when a service goes down
- **Network partition:** Verify behavior when services lose connectivity
- **Database corruption:** Verify recovery from corrupted SQLite files
- **Resource exhaustion:** Verify behavior under memory/CPU pressure

---

## 7. CI/CD Pipeline

Each service has its own GitHub Actions workflow:

| Step | Description |
|------|-------------|
| **Lint** | Run ruff/ESLint to check code style |
| **Type Check** | Run mypy (Python) or tsc (TypeScript) |
| **Unit Tests** | Run pytest/Jest |
| **Build** | Build Docker image |
| **Integration Tests** | Run against real services (on merge) |

Root CI pipeline orchestrates cross-service tests and manifest validation.

---

## 8. Test Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| API endpoints | 90%+ |
| Business logic | 95%+ |
| Utilities | 100% |
| Integration | Key paths covered |
| Security | All attack vectors tested |

Check coverage: `pytest --cov=hub --cov-report=term-missing`
