"""Shared test fixtures for ecosystem-wide tests."""

import os
import pytest


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
def headers(service: str):
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
