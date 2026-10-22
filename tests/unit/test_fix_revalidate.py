"""Unit tests for the fix-revalidate cycle."""

import os
import sys
import tempfile
import shutil
import unittest

# Add the Greenie directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Greenie"))

from hub.mission.models import (
    Mission,
    MissionMilestone,
    MissionFeature,
    ValidationResult,
    FeatureRole,
    FeatureStatus,
    MilestoneStatus,
    MissionStatus,
)
from hub.mission import storage as mission_storage
from hub.mission import controller


class TestFixRevalidateCycle(unittest.TestCase):
    """Tests for the fix-revalidate cycle in the mission controller."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = self.db_path

        import importlib
        importlib.reload(mission_storage)
        importlib.reload(controller)

    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def _create_mission_with_milestone(self):
        """Create a mission with one milestone."""
        milestone = MissionMilestone(
            id="ms-1",
            name="Test Milestone",
            description="A test milestone",
            status=MilestoneStatus.COMPLETED.value,
            features=[
                MissionFeature(
                    id="feat-1",
                    name="Feature 1",
                    role=FeatureRole.WORKER.value,
                    status=FeatureStatus.COMPLETED.value,
                )
            ],
        )
        mission = Mission(
            description="Test mission",
            target_repository="/test/repo",
            status=MissionStatus.VALIDATING.value,
            milestones=[milestone],
        )
        return mission_storage.save_mission(mission)

    def test_create_fix_features(self):
        """Fix features are created from validation findings."""
        mission = self._create_mission_with_milestone()

        # Add validation findings
        for i in range(3):
            result = ValidationResult(
                mission_id=mission.id,
                milestone_id="ms-1",
                severity="major",
                explanation=f"Test finding {i}",
                suggested_correction=f"Fix {i}",
            )
            mission_storage.save_validation_result(result)

        # Create fix features
        updated = controller.create_fix_features(mission.id, "ms-1")

        # Check that fix features were added
        ms = updated.milestones[0]
        fix_features = [f for f in ms.features if f.name.startswith("Fix:")]
        self.assertEqual(len(fix_features), 3)

        # Check milestone is back to executing
        self.assertEqual(ms.status, MilestoneStatus.EXECUTING.value)
        self.assertEqual(updated.status, MissionStatus.EXECUTING.value)

    def test_create_fix_features_filters_severity(self):
        """Only blocker/critical/major findings create fix features."""
        mission = self._create_mission_with_milestone()

        # Add findings of different severities
        for severity in ["blocker", "critical", "major", "minor", "info"]:
            result = ValidationResult(
                mission_id=mission.id,
                milestone_id="ms-1",
                severity=severity,
                explanation=f"{severity} finding",
            )
            mission_storage.save_validation_result(result)

        updated = controller.create_fix_features(mission.id, "ms-1")
        ms = updated.milestones[0]
        fix_features = [f for f in ms.features if f.name.startswith("Fix:")]
        # Only blocker, critical, major should create fix features
        self.assertEqual(len(fix_features), 3)

    def test_create_fix_features_skips_verified(self):
        """Verified findings don't create fix features."""
        mission = self._create_mission_with_milestone()

        result = ValidationResult(
            mission_id=mission.id,
            milestone_id="ms-1",
            severity="major",
            explanation="Verified finding",
            verified=True,
        )
        mission_storage.save_validation_result(result)

        result2 = ValidationResult(
            mission_id=mission.id,
            milestone_id="ms-1",
            severity="major",
            explanation="Unverified finding",
            verified=False,
        )
        mission_storage.save_validation_result(result2)

        updated = controller.create_fix_features(mission.id, "ms-1")
        ms = updated.milestones[0]
        fix_features = [f for f in ms.features if f.name.startswith("Fix:")]
        self.assertEqual(len(fix_features), 1)

    def test_create_fix_features_no_findings(self):
        """No fix features when there are no fixable findings."""
        mission = self._create_mission_with_milestone()
        updated = controller.create_fix_features(mission.id, "ms-1")

        ms = updated.milestones[0]
        fix_features = [f for f in ms.features if f.name.startswith("Fix:")]
        self.assertEqual(len(fix_features), 0)

    def test_create_fix_features_max_retries(self):
        """Mission fails after max retries exceeded."""
        mission = self._create_mission_with_milestone()

        # Set retry count to max
        mission.artifacts = [{"type": "fix_retry_count", "count": 3}]
        mission_storage.save_mission(mission)

        # Add a finding
        result = ValidationResult(
            mission_id=mission.id,
            milestone_id="ms-1",
            severity="major",
            explanation="Test finding",
        )
        mission_storage.save_validation_result(result)

        updated = controller.create_fix_features(mission.id, "ms-1")
        self.assertEqual(updated.status, MissionStatus.FAILED.value)
        self.assertIn("retries", updated.error)

    def test_create_fix_features_not_found(self):
        """Error when mission not found."""
        with self.assertRaises(ValueError):
            controller.create_fix_features("nonexistent", "ms-1")

    def test_create_fix_features_milestone_not_found(self):
        """Error when milestone not found."""
        mission = self._create_mission_with_milestone()
        with self.assertRaises(ValueError):
            controller.create_fix_features(mission.id, "nonexistent")

    def test_start_fix_revalidate(self):
        """Fix-revalidate cycle starts correctly."""
        mission = self._create_mission_with_milestone()

        # Add validation findings
        result = ValidationResult(
            mission_id=mission.id,
            milestone_id="ms-1",
            severity="critical",
            explanation="Critical issue",
            suggested_correction="Fix it",
        )
        mission_storage.save_validation_result(result)

        result = controller.start_fix_revalidate(mission.id, "ms-1")
        self.assertEqual(result["status"], "fix_features_created")
        self.assertEqual(result["fix_features_created"], 1)
        self.assertIn("mission", result)

    def test_start_fix_revalidate_custom_retries(self):
        """Custom max retries is respected."""
        mission = self._create_mission_with_milestone()

        result = ValidationResult(
            mission_id=mission.id,
            milestone_id="ms-1",
            severity="major",
            explanation="Test finding",
        )
        mission_storage.save_validation_result(result)

        result = controller.start_fix_revalidate(mission.id, "ms-1", max_retries=5)
        self.assertEqual(result["status"], "fix_features_created")

    def test_retry_count_tracking(self):
        """Retry count is tracked in artifacts."""
        mission = self._create_mission_with_milestone()

        # Add findings
        for i in range(2):
            result = ValidationResult(
                mission_id=mission.id,
                milestone_id="ms-1",
                severity="major",
                explanation=f"Finding {i}",
            )
            mission_storage.save_validation_result(result)

        # First retry
        controller.create_fix_features(mission.id, "ms-1")
        mission = mission_storage.get_mission(mission.id)

        retry_artifact = None
        for artifact in mission.artifacts:
            if artifact.get("type") == "fix_retry_count":
                retry_artifact = artifact
                break

        self.assertIsNotNone(retry_artifact)
        self.assertEqual(retry_artifact["count"], 1)


class TestMissionLogging(unittest.TestCase):
    """Tests for mission execution logging."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = self.db_path

        import importlib
        importlib.reload(mission_storage)
        importlib.reload(controller)

    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def test_create_mission_logs(self):
        """Creating a mission creates a log entry."""
        mission = controller.create_mission(
            description="Test mission",
            target_repository="/test/repo",
        )
        logs = mission_storage.get_mission_logs(mission.id)
        self.assertGreaterEqual(len(logs), 1)
        self.assertIn("Mission created", logs[0]["message"])

    def test_start_execution_logs(self):
        """Starting execution creates a log entry."""
        mission = controller.create_mission(
            description="Test",
            target_repository="/test/repo",
        )
        controller.start_execution(mission.id)
        logs = mission_storage.get_mission_logs(mission.id)
        execution_logs = [l for l in logs if "Execution started" in l["message"]]
        self.assertGreaterEqual(len(execution_logs), 1)

    def test_cancel_mission_logs(self):
        """Cancelling a mission creates a log entry."""
        mission = controller.create_mission(
            description="Test",
            target_repository="/test/repo",
        )
        controller.start_execution(mission.id)
        controller.cancel_mission(mission.id, "Test cancel")
        logs = mission_storage.get_mission_logs(mission.id)
        cancel_logs = [l for l in logs if "cancelled" in l["message"].lower()]
        self.assertGreaterEqual(len(cancel_logs), 1)


if __name__ == "__main__":
    unittest.main()
