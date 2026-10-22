"""Shared test fixtures for ecosystem-wide tests."""

import os
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as requiring live services (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests that require live services as integration tests."""
    # Tests that connect to localhost services are integration tests
    # We mark entire test modules based on their category
    integration_modules = {
        "test_integration",
        "test_security",
        "test_benchmarks",
        "test_evaluation",
        "test_mission_cross_service",
        "test_slammer_dashboard",
        "test_speedy_cli",
    }
    # Tests within integration modules that DON'T need live services
    non_integration_tests = {
        "test_report_generation",  # Pure unit test in evaluation module
    }
    for item in items:
        module_name = item.module.__name__ if hasattr(item, "module") and item.module else ""
        module_basename = module_name.split(".")[-1] if module_name else ""

        # Skip tests that are explicitly non-integration
        if item.name in non_integration_tests:
            continue

        # Mark integration, security, benchmarks, and evaluation tests
        if module_basename in integration_modules:
            item.add_marker(pytest.mark.integration)

        # Mark specific chaos tests that need services
        if module_basename == "test_chaos":
            # These tests don't need services
            chaos_non_integration = {
                "test_health_check_on_down_service",
                "test_request_timeout_handling",
                "test_dns_failure_handling",
            }
            if item.name not in chaos_non_integration:
                item.add_marker(pytest.mark.integration)

        # Mark slow tests
        slow_tests = {
            "test_rapid_requests",
            "test_many_secrets",
            "test_full_evaluation",
            "test_concurrent_writes",
            "test_read_during_write",
        }
        if item.name in slow_tests:
            item.add_marker(pytest.mark.slow)


# Service URLs from environment or defaults
SERVICES = {
    "greenie": os.getenv("EVERSHADE_GREENIE_URL", "http://localhost:8000"),
    "slinker": os.getenv("EVERSHADE_SLINKER_URL", "http://localhost:8001"),
    "trapper": os.getenv("EVERSHADE_TRAPPER_URL", "http://localhost:3000"),
    "gobber": os.getenv("EVERSHADE_GOBBER_URL", "http://localhost:8002"),
    "sneaker": os.getenv("EVERSHADE_SNEAKER_URL", "http://localhost:8003"),
    "hider": os.getenv("EVERSHADE_HIDER_URL", "http://localhost:8004"),
    "poltergeist": os.getenv("EVERSHADE_POLTERGEIST_URL", "http://localhost:8005"),
    "shrewd": os.getenv("EVERSHADE_SHREWD_URL", "http://localhost:8006"),
    "slammer": os.getenv("EVERSHADE_SLAMMER_URL", "http://localhost:5173"),
}

# API keys from environment or defaults
API_KEYS = {
    "greenie": os.getenv("EVERSHADE_GREENIE_API_TOKEN", "Greenie-dev-key-change-me"),
    "slinker": os.getenv("EVERSHADE_SLINKER_API_KEY", "Slinker-dev-key-change-me"),
    "trapper": os.getenv("EVERSHADE_TRAPPER_API_KEY", "Trapper-dev-key-change-me"),
    "gobber": os.getenv("EVERSHADE_GOBBER_API_KEY", "Gobber-dev-key-change-me"),
    "sneaker": os.getenv("EVERSHADE_SNEAKER_API_KEY", "Sneaker-dev-key-change-me"),
    "hider": os.getenv("EVERSHADE_HIDER_API_KEY", "Hider-dev-key-change-me"),
    "poltergeist": os.getenv("EVERSHADE_POLTERGEIST_API_KEY", "Poltergeist-dev-key-change-me"),
    "shrewd": os.getenv("EVERSHADE_SHREWD_API_KEY", "Shrewd-dev-key-change-me"),
}


@pytest.fixture
def headers(request, service: str):
    """Return Bearer auth headers for a given service."""
    return {
        "Authorization": f"Bearer {API_KEYS[service]}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def base_url(service: str):
    """Return the base URL for a given service."""
    return SERVICES[service]


@pytest.fixture(params=list(SERVICES.keys()))
def service(request):
    """Parametrized fixture that iterates over all services."""
    return request.param


@pytest.fixture
def all_services():
    """Return the dict of all service URLs."""
    return SERVICES


@pytest.fixture
def all_api_keys():
    """Return the dict of all API keys."""
    return API_KEYS
