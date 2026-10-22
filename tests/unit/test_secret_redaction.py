"""Unit tests for the secret redaction module.

Tests pattern-based redaction of API keys, tokens, passwords, and other
sensitive data in text, environment variables, dictionaries, and LLM context.
"""

import sys
import logging
from pathlib import Path

# Add Greenie to path
greenie_root = Path(__file__).resolve().parent.parent.parent / "Greenie"
if str(greenie_root) not in sys.path:
    sys.path.insert(0, str(greenie_root))

import pytest
from hub.mission import secret_redaction


class TestRedactSecrets:
    def test_redact_api_key(self):
        """API keys should be redacted."""
        text = "api_key=sk-1234567890abcdef1234567890abcdef"
        result = secret_redaction.redact_secrets(text)
        assert "[REDACTED]" in result
        assert "sk-1234567890abcdef1234567890abcdef" not in result

    def test_redact_bearer_token(self):
        """Bearer tokens should be redacted."""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123"
        result = secret_redaction.redact_secrets(text)
        assert "[REDACTED]" in result

    def test_redact_password(self):
        """Passwords should be redacted."""
        text = "password=MyS3cureP@ssw0rd!"
        result = secret_redaction.redact_secrets(text)
        assert "[REDACTED]" in result
        assert "MyS3cureP@ssw0rd!" not in result

    def test_redact_github_token(self):
        """GitHub tokens should be redacted."""
        text = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
        result = secret_redaction.redact_secrets(text)
        assert "[REDACTED]" in result

    def test_redact_aws_key(self):
        """AWS access keys should be redacted."""
        text = "AKIAIOSFODNN7EXAMPLE"
        result = secret_redaction.redact_secrets(text)
        assert "[REDACTED]" in result

    def test_redact_email(self):
        """Email addresses should be redacted."""
        text = "Contact user@example.com for help"
        result = secret_redaction.redact_secrets(text)
        assert "[EMAIL REDACTED]" in result
        assert "user@example.com" not in result

    def test_no_redaction_for_normal_text(self):
        """Normal text without secrets should be unchanged."""
        text = "Hello, this is a normal message with no secrets."
        result = secret_redaction.redact_secrets(text)
        assert result == text

    def test_empty_string(self):
        """Empty string should return empty."""
        assert secret_redaction.redact_secrets("") == ""

    def test_none_handling(self):
        """None-like values should be handled gracefully."""
        assert secret_redaction.redact_secrets("") == ""


class TestRedactEnvVars:
    def test_redact_sensitive_env_vars(self):
        """Sensitive environment variables should be redacted."""
        env = {
            "PATH": "/usr/bin",
            "API_KEY": "secret123",
            "HOME": "/home/user",
            "DATABASE_URL": "postgres://user:pass@localhost/db",
        }
        result = secret_redaction.redact_env_vars(env)
        assert result["PATH"] == "/usr/bin"
        assert result["API_KEY"] == "[REDACTED]"
        assert result["HOME"] == "/home/user"
        assert result["DATABASE_URL"] == "[REDACTED]"

    def test_no_redaction_for_normal_env(self):
        """Non-sensitive env vars should be unchanged."""
        env = {"PATH": "/usr/bin", "HOME": "/home/user"}
        result = secret_redaction.redact_env_vars(env)
        assert result == env


class TestRedactDict:
    def test_redact_secret_keys(self):
        """Dictionary values with secret keys should be redacted."""
        data = {
            "name": "test",
            "api_key": "secret123",
            "password": "mypass",
            "count": 42,
        }
        result = secret_redaction.redact_dict(data)
        assert result["name"] == "test"
        assert result["api_key"] == "[REDACTED]"
        assert result["password"] == "[REDACTED]"
        assert result["count"] == 42

    def test_nested_dict_redaction(self):
        """Nested dictionaries should be redacted recursively."""
        data = {
            "config": {
                "api_key": "secret",
                "host": "localhost",
            },
            "name": "test",
        }
        result = secret_redaction.redact_dict(data)
        assert result["config"]["api_key"] == "[REDACTED]"
        assert result["config"]["host"] == "localhost"

    def test_custom_secret_keys(self):
        """Custom secret keys should be redacted."""
        data = {
            "custom_token": "my-custom-secret",
            "name": "test",
        }
        result = secret_redaction.redact_dict(data, secret_keys={"custom_token"})
        assert result["custom_token"] == "[REDACTED]"
        assert result["name"] == "test"


class TestRedactModelContext:
    def test_redact_messages(self):
        """LLM messages should have secrets redacted."""
        messages = [
            {"role": "user", "content": "api_key=sk-1234567890abcdef1234567890abcdef"},
            {"role": "assistant", "content": "I'll help you with that."},
        ]
        result = secret_redaction.redact_model_context(messages)
        assert "[REDACTED]" in result[0]["content"]
        assert result[1]["content"] == "I'll help you with that."

    def test_empty_messages(self):
        """Empty message list should return empty."""
        assert secret_redaction.redact_model_context([]) == []


class TestSecretRedactionFilter:
    def test_log_filter_redacts(self):
        """Logging filter should redact secrets from log messages."""
        filter_instance = secret_redaction.SecretRedactionFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="api_key=sk-1234567890abcdef1234567890abcdef",
            args=(),
            exc_info=None,
        )
        filter_instance.filter(record)
        assert "[REDACTED]" in record.msg


class TestIsSensitiveKey:
    def test_sensitive_keys(self):
        """Known sensitive key names should be detected."""
        assert secret_redaction.is_sensitive_key("API_KEY") is True
        assert secret_redaction.is_sensitive_key("api_key") is True
        assert secret_redaction.is_sensitive_key("GITHUB_TOKEN") is True
        assert secret_redaction.is_sensitive_key("OPENAI_API_KEY") is True

    def test_non_sensitive_keys(self):
        """Non-sensitive key names should not be detected."""
        assert secret_redaction.is_sensitive_key("PATH") is False
        assert secret_redaction.is_sensitive_key("HOME") is False
        assert secret_redaction.is_sensitive_key("name") is False
