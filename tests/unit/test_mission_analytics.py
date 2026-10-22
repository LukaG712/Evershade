"""Unit tests for mission analytics module."""

import os
import sys
import tempfile
import shutil
import unittest
from unittest import mock

# Add the Greenie directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Greenie"))

from hub.mission.models import (
    Mission,
    MissionMilestone,
    MissionFeature,
    ValidationResult,
    ValidationSeverity,
    MissionStatus,
    MilestoneStatus,
)
from hub.mission import storage as mission_storage
from hub.mission import analytics as mission_analytics


class TestMissionAnalytics(unittest.TestCase):
    """Tests for mission analytics functions."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = self.db_path

        # Re-import storage to pick up the new DB path
        import importlib
        importlib.reload(mission_storage)
        importlib.reload(mission_analytics)

    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def _create_mission(self, status="completed", **kwargs):
        """Helper to create and save a mission."""
        mission = Mission(
            description=kwargs.get("description", "Test mission"),
            target_repository=kwargs.get("target_repository", "/test/repo"),
            status=status,
            orchestrator_model=kwargs.get("orchestrator_model", "gpt-4o"),
            worker_model=kwargs.get("worker_model", "gpt-4o-mini"),
            validator_model=kwargs.get("validator_model", "claude-3-sonnet"),
            autonomy_level=kwargs.get("autonomy_level", "restricted_autonomous"),
            milestones=kwargs.get("milestones", []),
            artifacts=kwargs.get("artifacts", []),
            created_at=kwargs.get("created_at", "2024-01-01T00:00:00+00:00"),
            started_at=kwargs.get("started_at", "2024-01-01T00:01:00+00:00"),
            completed_at=kwargs.get("completed_at", "2024-01-01T00:10:00+00:00"),
        )
        return mission_storage.save_mission(mission)

    def test_empty_analytics(self):
        """Analytics with no missions returns zeros."""
        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.total_missions, 0)
        self.assertEqual(summary.completed_missions, 0)
        self.assertEqual(summary.success_rate, 0.0)

    def test_analytics_with_missions(self):
        """Analytics correctly counts missions by status."""
        self._create_mission(status="completed")
        self._create_mission(status="completed")
        self._create_mission(status="failed")
        self._create_mission(status="planning")

        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.total_missions, 4)
        self.assertEqual(summary.completed_missions, 2)
        self.assertEqual(summary.failed_missions, 1)
        self.assertEqual(summary.success_rate, 2 / 3)  # 2 completed / (2 + 1 failed)

    def test_analytics_duration(self):
        """Analytics calculates average durations."""
        self._create_mission(
            status="completed",
            created_at="2024-01-01T00:00:00+00:00",
            started_at="2024-01-01T00:05:00+00:00",
            completed_at="2024-01-01T00:15:00+00:00",
        )

        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.avg_planning_duration_seconds, 300.0)  # 5 minutes
        self.assertEqual(summary.avg_execution_duration_seconds, 600.0)  # 10 minutes
        self.assertEqual(summary.avg_total_duration_seconds, 900.0)  # 15 minutes

    def test_analytics_model_usage(self):
        """Analytics tracks model usage per role."""
        self._create_mission(
            orchestrator_model="gpt-4o",
            worker_model="gpt-4o-mini",
            validator_model="claude-3-sonnet",
        )

        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.model_usage.get("orchestrator:gpt-4o"), 1)
        self.assertEqual(summary.model_usage.get("worker:gpt-4o-mini"), 1)
        self.assertEqual(summary.model_usage.get("validator:claude-3-sonnet"), 1)

    def test_analytics_autonomy_distribution(self):
        """Analytics tracks autonomy level distribution."""
        self._create_mission(autonomy_level="supervised")
        self._create_mission(autonomy_level="restricted_autonomous")
        self._create_mission(autonomy_level="full_autonomous")

        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.missions_by_autonomy.get("supervised"), 1)
        self.assertEqual(summary.missions_by_autonomy.get("restricted_autonomous"), 1)
        self.assertEqual(summary.missions_by_autonomy.get("full_autonomous"), 1)

    def test_analytics_validation_findings(self):
        """Analytics counts validation findings by severity."""
        mission = self._create_mission(status="completed")

        # Add validation results
        for severity in ["blocker", "critical", "major", "minor", "info"]:
            result = ValidationResult(
                mission_id=mission.id,
                severity=severity,
                explanation=f"Test {severity} finding",
            )
            mission_storage.save_validation_result(result)

        summary = mission_analytics.get_mission_analytics()
        self.assertEqual(summary.total_validation_findings, 5)
        self.assertEqual(summary.findings_by_severity.get("blocker"), 1)
        self.assertEqual(summary.findings_by_severity.get("critical"), 1)

    def test_analytics_to_dict(self):
        """Analytics summary serializes to dict."""
        summary = mission_analytics.get_mission_analytics()
        d = summary.to_dict()
        self.assertIn("total_missions", d)
        self.assertIn("success_rate", d)
        self.assertIn("avg_planning_duration_seconds", d)

    def test_mission_timeline(self):
        """Timeline is reconstructed from mission state."""
        mission = self._create_mission(
            status="completed",
            created_at="2024-01-01T00:00:00+00:00",
            started_at="2024-01-01T00:05:00+00:00",
            completed_at="2024-01-01T00:15:00+00:00",
        )

        timeline = mission_analytics.get_mission_timeline(mission.id)
        self.assertIsNotNone(timeline)
        self.assertEqual(timeline.mission_id, mission.id)
        self.assertGreater(len(timeline.transitions), 0)
        self.assertIn("planning", timeline.stage_durations)
        self.assertIn("execution", timeline.stage_durations)

    def test_mission_timeline_not_found(self):
        """Timeline returns None for non-existent mission."""
        timeline = mission_analytics.get_mission_timeline("nonexistent")
        self.assertIsNone(timeline)

    def test_mission_timeline_to_dict(self):
        """Timeline serializes to dict."""
        mission = self._create_mission()
        timeline = mission_analytics.get_mission_timeline(mission.id)
        d = timeline.to_dict()
        self.assertIn("mission_id", d)
        self.assertIn("transitions", d)
        self.assertIn("stage_durations", d)

    def test_validation_summary(self):
        """Validation summary counts findings by severity."""
        mission = self._create_mission()

        for _ in range(3):
            mission_storage.save_validation_result(
                ValidationResult(
                    mission_id=mission.id,
                    severity="major",
                    explanation="Test finding",
                    file_path="test.py",
                )
            )
        mission_storage.save_validation_result(
            ValidationResult(
                mission_id=mission.id,
                severity="info",
                explanation="Minor issue",
            )
        )

        summary = mission_analytics.get_validation_summary(mission.id)
        self.assertEqual(summary["total_findings"], 4)
        self.assertEqual(summary["severity_counts"].get("major"), 3)
        self.assertTrue(summary["passed"])  # No blockers or criticals

    def test_validation_summary_with_blockers(self):
        """Validation summary detects blockers."""
        mission = self._create_mission()
        mission_storage.save_validation_result(
            ValidationResult(
                mission_id=mission.id,
                severity="blocker",
                explanation="Critical issue",
            )
        )

        summary = mission_analytics.get_validation_summary(mission.id)
        self.assertTrue(summary["has_blockers"])
        self.assertFalse(summary["passed"])

    def test_validation_summary_with_criticals(self):
        """Validation summary detects criticals."""
        mission = self._create_mission()
        mission_storage.save_validation_result(
            ValidationResult(
                mission_id=mission.id,
                severity="critical",
                explanation="Critical issue",
            )
        )

        summary = mission_analytics.get_validation_summary(mission.id)
        self.assertTrue(summary["has_criticals"])
        self.assertFalse(summary["passed"])

    def test_recent_missions(self):
        """Recent missions returns list with key metrics."""
        self._create_mission(status="completed")
        self._create_mission(status="executing")

        recent = mission_analytics.get_recent_missions(limit=10)
        self.assertEqual(len(recent), 2)
        self.assertIn("id", recent[0])
        self.assertIn("status", recent[0])
        self.assertIn("duration_seconds", recent[0])

    def test_recent_missions_filter_by_status(self):
        """Recent missions filters by status."""
        self._create_mission(status="completed")
        self._create_mission(status="executing")
        self._create_mission(status="completed")

        recent = mission_analytics.get_recent_missions(status="completed")
        self.assertEqual(len(recent), 2)

    def test_parse_timestamp(self):
        """Timestamp parsing handles valid and invalid inputs."""
        from hub.mission.analytics import _parse_timestamp

        dt = _parse_timestamp("2024-01-01T00:00:00+00:00")
        self.assertIsNotNone(dt)

        self.assertIsNone(_parse_timestamp(None))
        self.assertIsNone(_parse_timestamp(""))
        self.assertIsNone(_parse_timestamp("not-a-date"))


class TestDurationCalculation(unittest.TestCase):
    """Tests for duration calculation helpers."""

    def test_duration_seconds(self):
        """Duration between two timestamps is correct."""
        from hub.mission.analytics import _duration_seconds

        dur = _duration_seconds(
            "2024-01-01T00:00:00+00:00",
            "2024-01-01T00:05:00+00:00",
        )
        self.assertEqual(dur, 300.0)

    def test_duration_none_input(self):
        """Duration returns None for missing timestamps."""
        from hub.mission.analytics import _duration_seconds

        self.assertIsNone(_duration_seconds(None, "2024-01-01T00:00:00+00:00"))
        self.assertIsNone(_duration_seconds("2024-01-01T00:00:00+00:00", None))


if __name__ == "__main__":
    unittest.main()
