# Evershade Testing Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. Test Structure

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
