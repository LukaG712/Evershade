"""Tests for rate limiting middleware."""

import time
import pytest
from unittest.mock import MagicMock, patch

from hub.api.rate_limit_middleware import (
    SlidingWindowRateLimiter,
    _get_rate_limit_key,
    _get_limit_for_path,
    _should_skip_rate_limit,
    _rate_limiter,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_DEFAULT_REQUESTS,
    RATE_LIMIT_DEFAULT_WINDOW,
)


class TestSlidingWindowRateLimiter:
    """Test the sliding window rate limiter."""

    def test_allow_within_limit(self):
        """Requests within limit should be allowed."""
        limiter = SlidingWindowRateLimiter()
        allowed, info = limiter.allow("test-key", 10, 60)
        assert allowed is True
        assert info["remaining"] == 9
        assert info["limit"] == 10

    def test_deny_after_limit(self):
        """Requests exceeding limit should be denied."""
        limiter = SlidingWindowRateLimiter()
        # Make 10 requests (the limit)
        for _ in range(10):
            allowed, _ = limiter.allow("test-key", 10, 60)
            assert allowed is True
        # 11th request should be denied
        allowed, info = limiter.allow("test-key", 10, 60)
        assert allowed is False
        assert info["remaining"] == 0
        assert info["retry_after"] > 0

    def test_different_keys_independent(self):
        """Different keys should have independent limits."""
        limiter = SlidingWindowRateLimiter()
        # Exhaust limit for key1
        for _ in range(5):
            limiter.allow("key1", 5, 60)
        allowed1, _ = limiter.allow("key1", 5, 60)
        assert allowed1 is False
        # key2 should still be allowed
        allowed2, _ = limiter.allow("key2", 5, 60)
        assert allowed2 is True

    def test_window_expiry(self):
        """Old requests should expire after window."""
        limiter = SlidingWindowRateLimiter()
        # Fill the limit
        for _ in range(5):
            limiter.allow("test-key", 5, 60)
        allowed, _ = limiter.allow("test-key", 5, 60)
        assert allowed is False
        # Simulate time passing beyond the window
        with patch("hub.api.rate_limit_middleware.time.time", return_value=time.time() + 61):
            allowed, info = limiter.allow("test-key", 5, 60)
            assert allowed is True
            assert info["remaining"] == 4

    def test_retry_after_calculation(self):
        """Retry-after should reflect time until oldest request expires."""
        limiter = SlidingWindowRateLimiter()
        for _ in range(5):
            limiter.allow("test-key", 5, 10)
        allowed, info = limiter.allow("test-key", 5, 10)
        assert allowed is False
        assert 1 <= info["retry_after"] <= 11


class TestRateLimitKeyExtraction:
    """Test rate limit key extraction from requests."""

    def test_bearer_token_key(self):
        """Bearer token should be hashed for rate limiting."""
        request = MagicMock()
        request.headers = {"authorization": "Bearer my-secret-token"}
        request.client = MagicMock(host="127.0.0.1")
        key = _get_rate_limit_key(request)
        assert key.startswith("apikey:")
        assert "my-secret-token" not in key  # Token should be hashed

    def test_ip_fallback(self):
        """IP address should be used when no Bearer token."""
        request = MagicMock()
        request.headers = {}
        request.client = MagicMock(host="192.168.1.1")
        key = _get_rate_limit_key(request)
        assert key == "ip:192.168.1.1"

    def test_different_tokens_different_keys(self):
        """Different API tokens should have different rate limit keys."""
        req1 = MagicMock()
        req1.headers = {"authorization": "Bearer token1"}
        req1.client = MagicMock(host="127.0.0.1")
        req2 = MagicMock()
        req2.headers = {"authorization": "Bearer token2"}
        req2.client = MagicMock(host="127.0.0.1")
        key1 = _get_rate_limit_key(req1)
        key2 = _get_rate_limit_key(req2)
        assert key1 != key2


class TestRateLimitPathMatching:
    """Test rate limit configuration for different paths."""

    def test_expensive_path_stricter_limit(self):
        """Expensive paths should have stricter limits."""
        max_req, window = _get_limit_for_path("/api/agents/run")
        assert max_req <= RATE_LIMIT_DEFAULT_REQUESTS

    def test_default_path_default_limit(self):
        """Non-expensive paths should use default limits."""
        max_req, window = _get_limit_for_path("/api/unknown")
        assert max_req == RATE_LIMIT_DEFAULT_REQUESTS
        assert window == RATE_LIMIT_DEFAULT_WINDOW

    def test_prefix_match(self):
        """Path prefix should match expensive path limits."""
        max_req, window = _get_limit_for_path("/api/agents/run/123")
        assert max_req <= RATE_LIMIT_DEFAULT_REQUESTS


class TestRateLimitSkipLogic:
    """Test when rate limiting should be skipped."""

    def test_skip_safe_methods(self):
        """GET, HEAD, OPTIONS should skip rate limiting."""
        for method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            request = MagicMock()
            request.method = method
            request.url = MagicMock(path="/api/agents/run")
            assert _should_skip_rate_limit(request) is True

    def test_skip_excluded_paths(self):
        """Health and metrics paths should skip rate limiting."""
        for path in ("/health", "/api/health", "/api/metrics", "/docs"):
            request = MagicMock()
            request.method = "POST"
            request.url = MagicMock(path=path)
            with patch("hub.api.rate_limit_middleware.RATE_LIMIT_ENABLED", True):
                assert _should_skip_rate_limit(request) is True

    def test_skip_when_disabled(self):
        """Rate limiting should be skipped when globally disabled."""
        request = MagicMock()
        request.method = "POST"
        request.url = MagicMock(path="/api/agents/run")
        with patch("hub.api.rate_limit_middleware.RATE_LIMIT_ENABLED", False):
            assert _should_skip_rate_limit(request) is True

    def test_not_skip_expensive_post(self):
        """POST to expensive path should not skip rate limiting."""
        request = MagicMock()
        request.method = "POST"
        request.url = MagicMock(path="/api/agents/run")
        with patch("hub.api.rate_limit_middleware.RATE_LIMIT_ENABLED", True):
            assert _should_skip_rate_limit(request) is False
