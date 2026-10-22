# Evershade Testing Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. Test Structure

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

---

## 2. Running Tests

### Individual Service

```bash
# Python services
cd Greenie
pip install -e ".[test]"
pytest -v

# TypeScript services
cd Trapper
npm install
npm test
```

### All Services

```bash
# Run tests for all services with local code
./tests/run-all-tests.sh
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

## 3. Integration Tests

Integration tests start the actual services and verify cross-service communication.

```bash
# Start test environment
docker compose --profile standard up -d

# Run all ecosystem tests
cd tests
./run-all-tests.sh all

# Run a specific category
./run-all-tests.sh integration
./run-all-tests.sh security
./run-all-tests.sh benchmarks
./run-all-tests.sh evaluation
./run-all-tests.sh chaos

# Or use pytest directly
pytest integration/ -v
pytest security/ -v
```

### Test Categories

| Category | Location | Tests | Description |
|----------|----------|-------|-------------|
| **Integration** | `tests/integration/` | 15+ | Cross-service communication, health checks, Bearer auth, secrets, chat, notifications, cache, metrics, agents, workflows |
| **Security** | `tests/security/` | 15+ | Prompt injection, SSRF, auth bypass, XSS, rate limiting, encryption at rest |
| **Benchmarks** | `tests/benchmarks/` | 10+ | API latency, throughput, concurrency, response sizes, error handling |
| **Evaluation** | `tests/evaluation/` | 8+ | Agent quality: QA, code gen, summarization, math, safety, JSON, translation |
| **Chaos** | `tests/chaos/` | 12+ | Service crash, network failure, data integrity, malformed input, resource exhaustion |
| **MCP/Plugins** | `Greenie/tests/` | 5+ | MCP server connectivity, plugin lifecycle, tool calling |

---

## 4. Release Signing

```bash
# Sign all artifacts for a release
python scripts/release_sign.py --version 1.5.0 --sign-all --secret "your-key"

# Verify a release
python scripts/verify_release.py --release release/ --secret "your-key"
```

Outputs: `checksums.txt`, `signatures.json`, `provenance.json` (SLSA-style)

---

## 5. CI/CD

Each service has its own GitHub Actions workflow. The root repository runs ecosystem-wide integration tests.

**Per-service CI:**
- Lint and format check
- Type checking (where applicable)
- Unit tests
- Build verification

**Ecosystem CI:**
- Service startup and health checks
- Cross-service API compatibility
- Workflow execution
- Backup and restore

---

## 6. Writing Tests

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

## 7. Test Data

- Use deterministic test fixtures, not random data
- Fake LLM providers for routine CI (no API costs)
- Real services for integration tests
- Clean up test data after each test
