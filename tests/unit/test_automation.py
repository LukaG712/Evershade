"""Unit tests for the automation engine.

Tests webhook handling, idempotency, rate limiting, schedule triggers,
and action registry.
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

# Add Greenie to path
greenie_root = Path(__file__).resolve().parent.parent.parent / "Greenie"
if str(greenie_root) not in sys.path:
    sys.path.insert(0, str(greenie_root))

import pytest
from hub.mission import automation
from hub.mission import storage as mission_storage


@pytest.fixture(autouse=True)
def use_temp_db():
    """Use a temporary database for each test."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    with patch.object(mission_storage, "_DB_PATH", db_path):
        mission_storage._init_schema()
        yield
    Path(db_path).unlink(missing_ok=True)
    wal_path = Path(db_path + "-wal")
    wal_path.unlink(missing_ok=True)
    shm_path = Path(db_path + "-shm")
    shm_path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def reset_automation_state():
    """Reset automation module state before each test."""
    automation._idempotency_store.clear()
    automation._rate_limit_store.clear()
    automation._schedule_triggers.clear()
    automation.ACTION_REGISTRY.clear()
    automation._webhook_secret = None
    yield
    automation._idempotency_store.clear()
    automation._rate_limit_store.clear()
    automation._schedule_triggers.clear()
    automation.ACTION_REGISTRY.clear()
    automation._webhook_secret = None


class TestWebhookSignature:
    def test_verify_signature_without_secret(self):
        """Without a secret, verification should pass (with warning)."""
        result = automation.verify_webhook_signature(b"payload", "sha256=abc123")
        assert result is True

    def test_verify_signature_with_secret(self):
        """With a secret, valid signature should pass."""
        import hmac
        import hashlib
        automation.set_webhook_secret("my-secret")
        payload = b'{"test": "data"}'
        sig = "sha256=" + hmac.new(
            b"my-secret", payload, hashlib.sha256
        ).hexdigest()
        assert automation.verify_webhook_signature(payload, sig) is True

    def test_verify_signature_invalid(self):
        """Invalid signature should fail."""
        automation.set_webhook_secret("my-secret")
        payload = b'{"test": "data"}'
        assert automation.verify_webhook_signature(payload, "sha256=invalid") is False

    def test_verify_signature_missing_prefix(self):
        """Signature without sha256= prefix should fail."""
        automation.set_webhook_secret("my-secret")
        assert automation.verify_webhook_signature(b"payload", "abc123") is False


class TestIdempotency:
    def test_duplicate_issue_event(self):
        """Duplicate issue events should return the existing mission."""
        payload = {
            "X-GitHub-Event": "issues",
            "action": "opened",
            "id": "event-1",
            "sender": {"login": "user1"},
            "issue": {
                "number": 42,
                "title": "Test issue",
                "body": "Body",
                "labels": [],
            },
            "repository": {"full_name": "owner/repo"},
        }
        result1 = automation.handle_github_webhook(payload)
        assert result1["status"] == "created"
        mission_id = result1["mission_id"]

        result2 = automation.handle_github_webhook(payload)
        assert result2["status"] == "duplicate"
        assert result2["mission_id"] == mission_id

    def test_duplicate_pr_event(self):
        """Duplicate PR events should return the existing mission."""
        payload = {
            "X-GitHub-Event": "pull_request",
            "action": "opened",
            "id": "pr-event-1",
            "sender": {"login": "user1"},
            "pull_request": {
                "number": 10,
                "title": "Fix bug",
                "body": "PR body",
            },
            "repository": {"full_name": "owner/repo"},
        }
        result1 = automation.handle_github_webhook(payload)
        assert result1["status"] == "created"

        result2 = automation.handle_github_webhook(payload)
        assert result2["status"] == "duplicate"

    def test_expired_idempotency_entry(self):
        """Expired idempotency entries should allow re-creation."""
        payload = {
            "X-GitHub-Event": "issues",
            "action": "opened",
            "id": "event-expire",
            "sender": {"login": "user1"},
            "issue": {
                "number": 1,
                "title": "Expire test",
                "body": "",
                "labels": [],
            },
            "repository": {"full_name": "owner/repo"},
        }
        result1 = automation.handle_github_webhook(payload)
        assert result1["status"] == "created"

        # Manually expire the entry
        event_hash = automation._compute_event_hash("opened", "event-expire", "Expire test", "1")
        automation._idempotency_store[event_hash] = (result1["mission_id"], time.time() - 600)

        result2 = automation.handle_github_webhook(payload)
        assert result2["status"] == "created"

    def test_cleanup_idempotency_store(self):
        """Cleanup should remove expired entries."""
        automation._idempotency_store["key1"] = ("mission-1", time.time() - 600)
        automation._idempotency_store["key2"] = ("mission-2", time.time())
        removed = automation.cleanup_idempotency_store()
        assert removed == 1
        assert "key1" not in automation._idempotency_store
        assert "key2" in automation._idempotency_store


class TestRateLimiting:
    def test_rate_limit_exceeded(self):
        """Exceeding rate limit should return rate_limited status."""
        automation._rate_limit_max = 3
        # First 3 should succeed
        for i in range(3):
            payload = {
                "X-GitHub-Event": "issues",
                "action": "opened",
                "id": f"rate-{i}",
                "sender": {"login": "limited-user"},
                "issue": {
                    "number": i,
                    "title": f"Rate test {i}",
                    "body": "",
                    "labels": [],
                },
                "repository": {"full_name": "owner/repo"},
            }
            result = automation.handle_github_webhook(payload)
            assert result["status"] == "created", f"Request {i} should succeed"

        # 4th should be rate limited
        payload = {
            "X-GitHub-Event": "issues",
            "action": "opened",
            "id": "rate-3",
            "sender": {"login": "limited-user"},
            "issue": {
                "number": 3,
                "title": "Rate test 3",
                "body": "",
                "labels": [],
            },
            "repository": {"full_name": "owner/repo"},
        }
        result = automation.handle_github_webhook(payload)
        assert result["status"] == "rate_limited"

    def test_different_sources_not_rate_limited(self):
        """Different sources should have independent rate limits."""
        automation._rate_limit_max = 2
        for i in range(2):
            payload = {
                "X-GitHub-Event": "issues",
                "action": "opened",
                "id": f"src1-{i}",
                "sender": {"login": "source1"},
                "issue": {"number": i, "title": f"Test {i}", "body": "", "labels": []},
                "repository": {"full_name": "owner/repo"},
            }
            automation.handle_github_webhook(payload)

        # Different source should not be limited
        payload = {
            "X-GitHub-Event": "issues",
            "action": "opened",
            "id": "src2-0",
            "sender": {"login": "source2"},
            "issue": {"number": 0, "title": "Test", "body": "", "labels": []},
            "repository": {"full_name": "owner/repo"},
        }
        result = automation.handle_github_webhook(payload)
        assert result["status"] == "created"


class TestScheduleTriggers:
    def test_register_trigger(self):
        """Registering a trigger should add it to the list."""
        def dummy_action():
            return {"status": "ok"}

        automation.register_schedule_trigger("daily-cleanup", "0 2 * * *", dummy_action)
        triggers = automation.get_schedule_triggers()
        assert len(triggers) == 1
        assert triggers[0]["name"] == "daily-cleanup"
        assert triggers[0]["cron"] == "0 2 * * *"
        assert triggers[0]["enabled"] is True

    def test_duplicate_trigger_name(self):
        """Registering a duplicate name should raise ValueError."""
        automation.register_schedule_trigger("test", "0 * * * *", lambda: {})
        with pytest.raises(ValueError, match="already registered"):
            automation.register_schedule_trigger("test", "0 * * * *", lambda: {})

    def test_remove_trigger(self):
        """Removing a trigger should remove it from the list."""
        automation.register_schedule_trigger("test", "0 * * * *", lambda: {})
        assert automation.remove_schedule_trigger("test") is True
        assert len(automation.get_schedule_triggers()) == 0

    def test_remove_nonexistent_trigger(self):
        """Removing a nonexistent trigger should return False."""
        assert automation.remove_schedule_trigger("nonexistent") is False

    def test_toggle_trigger(self):
        """Toggling a trigger should change its enabled state."""
        automation.register_schedule_trigger("test", "0 * * * *", lambda: {})
        assert automation.toggle_schedule_trigger("test", False) is True
        triggers = automation.get_schedule_triggers()
        assert triggers[0]["enabled"] is False

    def test_evaluate_triggers(self):
        """Evaluating triggers should execute due triggers."""
        call_count = 0
        def counting_action():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        automation.register_schedule_trigger("counter", "* * * * *", counting_action)
        results = automation.evaluate_schedule_triggers()
        assert len(results) == 1
        assert results[0]["status"] == "executed"
        assert call_count == 1

    def test_disabled_trigger_not_executed(self):
        """Disabled triggers should not be executed."""
        call_count = 0
        def counting_action():
            nonlocal call_count
            call_count += 1
            return {}

        automation.register_schedule_trigger("disabled", "* * * * *", counting_action, enabled=False)
        results = automation.evaluate_schedule_triggers()
        assert len(results) == 0
        assert call_count == 0

    def test_trigger_error_handling(self):
        """Failed triggers should return error status."""
        def failing_action():
            raise RuntimeError("Test failure")

        automation.register_schedule_trigger("failing", "* * * * *", failing_action)
        results = automation.evaluate_schedule_triggers()
        assert len(results) == 1
        assert results[0]["status"] == "error"
        assert "Test failure" in results[0]["error"]


class TestActionRegistry:
    def test_register_and_execute_action(self):
        """Registered actions should be executable."""
        def my_action(x: int) -> int:
            return x * 2

        automation.register_action("double", my_action)
        assert "double" in automation.get_registered_actions()
        result = automation.execute_action("double", x=5)
        assert result == 10

    def test_execute_unregistered_action(self):
        """Executing an unregistered action should raise ValueError."""
        with pytest.raises(ValueError, match="not registered"):
            automation.execute_action("nonexistent")


class TestCIFailureWebhook:
    def test_ci_failure_creates_mission(self):
        """CI failure webhook should create a mission."""
        payload = {
            "X-GitHub-Event": "check_suite",
            "action": "completed",
            "id": "ci-1",
            "sender": {"login": "github-actions"},
            "check_suite": {
                "id": 12345,
                "status": "completed",
                "conclusion": "failure",
            },
            "repository": {"full_name": "owner/repo"},
        }
        result = automation.handle_github_webhook(payload)
        assert result["status"] == "created"

    def test_ci_success_ignored(self):
        """CI success should be ignored."""
        payload = {
            "X-GitHub-Event": "check_suite",
            "action": "completed",
            "id": "ci-2",
            "sender": {"login": "github-actions"},
            "check_suite": {
                "id": 12345,
                "status": "completed",
                "conclusion": "success",
            },
            "repository": {"full_name": "owner/repo"},
        }
        result = automation.handle_github_webhook(payload)
        assert result["status"] == "ignored"
