"""Unit tests for mission execution logs and SSE streaming."""

import asyncio
import os
import sys
import tempfile
import shutil
import unittest

# Add the Greenie directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Greenie"))

from hub.mission.models import Mission
from hub.mission import storage as mission_storage


class TestMissionLogs(unittest.TestCase):
    """Tests for mission execution log storage."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = self.db_path

        import importlib
        importlib.reload(mission_storage)

    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def test_save_and_get_logs(self):
        """Logs can be saved and retrieved."""
        mission_id = "test-mission-1"
        mission_storage.save_mission_log(mission_id, "info", "Test log message", "test")
        mission_storage.save_mission_log(mission_id, "error", "Error message", "test")

        logs = mission_storage.get_mission_logs(mission_id)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["level"], "error")  # Newest first
        self.assertEqual(logs[1]["level"], "info")

    def test_logs_have_timestamp(self):
        """Log entries have timestamps."""
        mission_id = "test-mission-2"
        mission_storage.save_mission_log(mission_id, "info", "Message")

        logs = mission_storage.get_mission_logs(mission_id)
        self.assertIn("timestamp", logs[0])
        self.assertIn("20", logs[0]["timestamp"])  # Year starts with 20

    def test_logs_filter_by_level(self):
        """Logs can be filtered by level."""
        mission_id = "test-mission-3"
        mission_storage.save_mission_log(mission_id, "info", "Info message")
        mission_storage.save_mission_log(mission_id, "error", "Error message")
        mission_storage.save_mission_log(mission_id, "info", "Another info")

        info_logs = mission_storage.get_mission_logs(mission_id, level="info")
        self.assertEqual(len(info_logs), 2)

        error_logs = mission_storage.get_mission_logs(mission_id, level="error")
        self.assertEqual(len(error_logs), 1)

    def test_logs_pagination(self):
        """Logs support pagination."""
        mission_id = "test-mission-4"
        for i in range(10):
            mission_storage.save_mission_log(mission_id, "info", f"Message {i}")

        page1 = mission_storage.get_mission_logs(mission_id, limit=5, offset=0)
        self.assertEqual(len(page1), 5)

        page2 = mission_storage.get_mission_logs(mission_id, limit=5, offset=5)
        self.assertEqual(len(page2), 5)

    def test_logs_since_timestamp(self):
        """Logs can be fetched since a timestamp."""
        mission_id = "test-mission-5"
        mission_storage.save_mission_log(mission_id, "info", "Old message")

        # Get the timestamp of the first log
        all_logs = mission_storage.get_mission_logs(mission_id)
        since = all_logs[0]["timestamp"]

        # Add a new log
        mission_storage.save_mission_log(mission_id, "info", "New message")

        # Fetch logs since the old timestamp
        new_logs = mission_storage.get_mission_logs_since(mission_id, since)
        self.assertGreaterEqual(len(new_logs), 1)

    def test_delete_logs(self):
        """Logs can be deleted by mission ID."""
        mission_id = "test-mission-6"
        mission_storage.save_mission_log(mission_id, "info", "Message 1")
        mission_storage.save_mission_log(mission_id, "info", "Message 2")

        deleted = mission_storage.delete_mission_logs(mission_id)
        self.assertEqual(deleted, 2)

        remaining = mission_storage.get_mission_logs(mission_id)
        self.assertEqual(len(remaining), 0)

    def test_empty_logs(self):
        """Empty logs list for non-existent mission."""
        logs = mission_storage.get_mission_logs("nonexistent")
        self.assertEqual(len(logs), 0)


class TestSSEStreaming(unittest.TestCase):
    """Tests for SSE streaming functionality."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = self.db_path

        import importlib
        importlib.reload(mission_storage)
        from hub.mission import sse as mission_sse
        self.sse = mission_sse

    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def test_format_sse(self):
        """SSE messages are properly formatted."""
        msg = self.sse.format_sse({"key": "value"}, event="test")
        self.assertIn("event: test", msg)
        self.assertIn("data:", msg)
        self.assertIn('"key": "value"', msg)

    def test_stream_mission_not_found(self):
        """SSE stream returns error for non-existent mission."""
        async def collect():
            result = []
            async for chunk in self.sse.stream_mission_logs("nonexistent"):
                result.append(chunk)
            return result

        results = asyncio.run(collect())
        combined = "".join(results)
        self.assertIn("error", combined)
        self.assertIn("Mission not found", combined)

    def test_stream_connected_event(self):
        """SSE stream sends connected event on start."""
        mission = Mission(
            description="Test",
            target_repository="/test/repo",
        )
        mission_storage.save_mission(mission)

        async def collect():
            result = []
            async for chunk in self.sse.stream_mission_logs(mission.id):
                result.append(chunk)
                if "connected" in chunk:
                    break
            return result

        results = asyncio.run(collect())
        combined = "".join(results)
        self.assertIn("connected", combined)

    def test_stream_terminal_status(self):
        """SSE stream closes for terminal status missions."""
        mission = Mission(
            description="Test",
            target_repository="/test/repo",
            status="completed",
        )
        mission_storage.save_mission(mission)

        async def collect():
            result = []
            async for chunk in self.sse.stream_mission_logs(mission.id):
                result.append(chunk)
            return result

        results = asyncio.run(collect())
        combined = "".join(results)
        self.assertIn("complete", combined)


if __name__ == "__main__":
    unittest.main()
