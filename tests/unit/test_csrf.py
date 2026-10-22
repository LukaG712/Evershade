"""Tests for CSRF protection middleware."""

import os
import pytest
from unittest.mock import patch, MagicMock

from hub.api.csrf import (
    generate_csrf_token,
    validate_csrf_token,
    get_csrf_token_from_request,
    should_skip_csrf,
    CSRF_ENABLED,
    CSRF_SECRET_KEY,
    CSRF_TOKEN_EXPIRY,
    CSRF_EXCLUDED_PATHS,
)


class TestCSRFTokenGeneration:
    """Test CSRF token generation and validation."""

    def test_generate_token_returns_string(self):
        """Token generation should return a non-empty string."""
        token = generate_csrf_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_format(self):
        """Token should have the expected format with dots."""
        token = generate_csrf_token()
        parts = token.split(".")
        assert len(parts) >= 2  # At least random.timestamp

    def test_generate_token_uniqueness(self):
        """Each generated token should be unique."""
        tokens = [generate_csrf_token() for _ in range(10)]
        assert len(set(tokens)) == 10

    def test_validate_valid_token(self):
        """Valid token should pass validation."""
        token = generate_csrf_token()
        assert validate_csrf_token(token) is True

    def test_validate_empty_token(self):
        """Empty token should fail validation."""
        assert validate_csrf_token("") is False

    def test_validate_none_token(self):
        """None token should fail validation."""
        assert validate_csrf_token(None) is False

    def test_validate_malformed_token(self):
        """Malformed token should fail validation."""
        assert validate_csrf_token("invalid") is False
        assert validate_csrf_token("a.b.c.d.e.f") is False  # Too many parts without proper format

    @patch("hub.api.csrf.CSRF_TOKEN_EXPIRY", 0)
    def test_validate_expired_token(self):
        """Expired token should fail validation."""
        import time
        # Generate a token, then patch expiry to 0 to make it expired
        with patch("hub.api.csrf.time.time", return_value=time.time() + 3601):
            assert validate_csrf_token(generate_csrf_token()) is False

    def test_validate_token_with_signature(self):
        """Token with HMAC signature should validate correctly."""
        with patch("hub.api.csrf.CSRF_SECRET_KEY", "test-secret-key"):
            token = generate_csrf_token()
            assert validate_csrf_token(token) is True
            # Token should have 3 parts: random.timestamp.signature
            parts = token.split(".")
            assert len(parts) == 3


class TestCSRFTokenExtraction:
    """Test CSRF token extraction from requests."""

    def test_extract_from_header(self):
        """Token should be extracted from X-CSRF-Token header."""
        request = MagicMock()
        request.headers = {"x-csrf-token": "test-token-123"}
        request.cookies = {}
        token = get_csrf_token_from_request(request)
        assert token == "test-token-123"

    def test_extract_from_alternative_header(self):
        """Token should be extracted from X-XSRF-Token header."""
        request = MagicMock()
        request.headers = {"x-xsrf-token": "test-token-456"}
        request.cookies = {}
        token = get_csrf_token_from_request(request)
        assert token == "test-token-456"

    def test_extract_from_cookie(self):
        """Token should be extracted from csrf_token cookie."""
        request = MagicMock()
        request.headers = {}
        request.cookies = {"csrf_token": "test-token-789"}
        token = get_csrf_token_from_request(request)
        assert token == "test-token-789"

    def test_header_takes_precedence(self):
        """Header token should take precedence over cookie."""
        request = MagicMock()
        request.headers = {"x-csrf-token": "header-token"}
        request.cookies = {"csrf_token": "cookie-token"}
        token = get_csrf_token_from_request(request)
        assert token == "header-token"

    def test_no_token_returns_none(self):
        """Missing token should return None."""
        request = MagicMock()
        request.headers = {}
        request.cookies = {}
        token = get_csrf_token_from_request(request)
        assert token is None


class TestCSRFSkipLogic:
    """Test CSRF skip logic for safe methods and excluded paths."""

    def test_skip_get_method(self):
        """GET requests should skip CSRF check."""
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            assert should_skip_csrf(request) is True

    def test_skip_head_method(self):
        """HEAD requests should skip CSRF check."""
        request = MagicMock()
        request.method = "HEAD"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            assert should_skip_csrf(request) is True

    def test_skip_options_method(self):
        """OPTIONS requests should skip CSRF check."""
        request = MagicMock()
        request.method = "OPTIONS"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            assert should_skip_csrf(request) is True

    def test_skip_health_path(self):
        """Health endpoint should skip CSRF check."""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/health"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            with patch("hub.api.csrf.CSRF_EXCLUDED_PATHS", {"/health", "/api/metrics"}):
                assert should_skip_csrf(request) is True

    def test_skip_metrics_path(self):
        """Metrics endpoint should skip CSRF check."""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/metrics"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            with patch("hub.api.csrf.CSRF_EXCLUDED_PATHS", {"/health", "/api/metrics"}):
                assert should_skip_csrf(request) is True

    def test_no_skip_post_method(self):
        """POST requests should not skip CSRF check."""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            with patch("hub.api.csrf.CSRF_EXCLUDED_PATHS", {"/health", "/api/metrics"}):
                assert should_skip_csrf(request) is False

    def test_no_skip_delete_method(self):
        """DELETE requests should not skip CSRF check."""
        request = MagicMock()
        request.method = "DELETE"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", True):
            with patch("hub.api.csrf.CSRF_EXCLUDED_PATHS", {"/health", "/api/metrics"}):
                assert should_skip_csrf(request) is False

    def test_disabled_csrf_skips_all(self):
        """Disabled CSRF should skip all requests."""
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/api/test"
        with patch("hub.api.csrf.CSRF_ENABLED", False):
            assert should_skip_csrf(request) is True


class TestCSRFConfiguration:
    """Test CSRF configuration."""

    def test_default_excluded_paths(self):
        """Default excluded paths should include health and metrics."""
        assert "/health" in CSRF_EXCLUDED_PATHS
        assert "/api/metrics" in CSRF_EXCLUDED_PATHS

    def test_token_expiry_positive(self):
        """Token expiry should be a positive integer."""
        assert CSRF_TOKEN_EXPIRY > 0

    def test_csrf_enabled_type(self):
        """CSRF_ENABLED should be a boolean."""
        assert isinstance(CSRF_ENABLED, bool)
