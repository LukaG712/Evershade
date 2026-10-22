"""End-to-end smoke test for the mission control system.

This test creates a mission against a test repository, runs planning,
executes a simple milestone, validates the result, and generates a
completion report — all without requiring Junie CLI or external services.
"""

import os
from pathlib import Path

import pytest

from hub.mission.models import (
    MissionStatus,
    ValidationSeverity,
    ValidationResult,
    AutonomyLevel,
)
from hub.mission import storage as mission_storage
from hub.mission import controller
from hub.mission.planner import plan_mission
from hub.mission.repo_intelligence import analyze_repository


class TestSmokeTest:
    """End-to-end smoke test using the mission controller functions."""

    @pytest.fixture(autouse=True)
    def _temp_db(self, tmp_path):
        """Use a temporary database for each test."""
        import importlib
        db_path = str(tmp_path / "test_missions.db")
        os.environ["GREENIE_MISSION_DB_PATH"] = db_path
        # Reload the storage module to pick up the new DB path
        mission_storage._DB_PATH = db_path
        importlib.reload(mission_storage)
        # Reload controller to use the reloaded storage
        import hub.mission.controller as ctrl
        importlib.reload(ctrl)
        yield
        os.environ.pop("GREENIE_MISSION_DB_PATH", None)

    def _create_test_repo(self, tmp_path: Path) -> Path:
        """Create a minimal test repository for the smoke test."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()
        (repo_dir / "README.md").write_text("# Test Repository\n\nA test repo for smoke testing.\n")
        (repo_dir / "main.py").write_text('def hello():\n    return "Hello, World!"\n')
        (repo_dir / "requirements.txt").write_text("requests>=2.28\n")
        return repo_dir

    def test_full_mission_lifecycle(self, tmp_path):
        """Run a complete mission lifecycle: create → plan → execute → validate → complete."""
        repo_dir = self._create_test_repo(tmp_path)

        # 1. Create mission
        mission = controller.create_mission(
            description="Add a greeting function to main.py",
            target_repository=str(repo_dir),
            autonomy_level=AutonomyLevel.RESTRICTED.value,
        )
        assert mission is not None
        assert mission.status == MissionStatus.PLANNING.value
        mission_id = mission.id

        # 2. Analyze repository
        repo_info = analyze_repository(str(repo_dir))
        assert repo_info is not None

        # 3. Create plan (heuristic fallback since Shrewd is not available)
        plan = plan_mission(
            description=mission.description,
            repo_path=str(repo_dir),
            orchestrator_model=None,
        )
        assert plan is not None
        assert "milestones" in plan
        assert len(plan["milestones"]) > 0

        # 4. Apply plan to mission
        controller.apply_plan(
            mission_id,
            plan["milestones"],
            plan.get("validation_contract"),
        )
        mission = mission_storage.get_mission(mission_id)
        assert mission is not None
        assert len(mission.milestones) > 0
        assert mission.status == MissionStatus.PLANNING.value

        # 5. Start execution
        controller.start_execution(mission_id)
        mission = mission_storage.get_mission(mission_id)
        assert mission.status == MissionStatus.EXECUTING.value

        # 6. Complete the first milestone
        first_milestone = mission.milestones[0]
        controller.complete_milestone(mission_id, first_milestone.id)
        mission = mission_storage.get_mission(mission_id)

        # 7. Add a validation result
        validation = ValidationResult(
            mission_id=mission_id,
            severity=ValidationSeverity.INFO.value,
            file_path="main.py",
            line_number=1,
            explanation="Greeting function added successfully",
            suggested_correction="",
            verified=True,
        )
        controller.add_validation_result(mission_id, validation)

        # 8. Verify logs were created
        logs = mission_storage.get_mission_logs(mission_id)
        assert len(logs) > 0
        log_messages = [log["message"] for log in logs]
        assert any("created" in msg.lower() for msg in log_messages)

        # 9. Verify checkpoint was saved
        checkpoint = mission_storage.get_latest_checkpoint(mission_id)
        assert checkpoint is not None

    def test_mission_with_validation_failure(self, tmp_path):
        """Test mission lifecycle with validation failure and fix."""
        repo_dir = self._create_test_repo(tmp_path)

        # Create and plan mission
        mission = controller.create_mission(
            description="Add error handling to main.py",
            target_repository=str(repo_dir),
        )
        mission_id = mission.id

        # Create a simple plan
        plan = plan_mission(
            description=mission.description,
            repo_path=str(repo_dir),
        )
        controller.apply_plan(mission_id, plan["milestones"], plan.get("validation_contract"))

        # Start execution
        controller.start_execution(mission_id)
        mission = mission_storage.get_mission(mission_id)

        # Complete milestone
        if mission.milestones:
            controller.complete_milestone(mission_id, mission.milestones[0].id)

        # Add a validation failure
        failure = ValidationResult(
            mission_id=mission_id,
            severity=ValidationSeverity.MAJOR.value,
            file_path="main.py",
            line_number=1,
            explanation="Missing error handling",
            suggested_correction="Add try/except block",
            verified=False,
        )
        controller.add_validation_result(mission_id, failure)

        # Create fix features (need a milestone_id)
        mission = mission_storage.get_mission(mission_id)
        if mission.milestones:
            updated = controller.create_fix_features(mission_id, mission.milestones[0].id)
            # Check that fix features were added to the milestone
            ms = updated.milestones[0]
            fix_count = sum(1 for f in ms.features if f.name.startswith("Fix:"))
            assert fix_count > 0

    def test_mission_cancel_and_resume(self, tmp_path):
        """Test mission cancellation and resume from checkpoint."""
        repo_dir = self._create_test_repo(tmp_path)

        # Create mission
        mission = controller.create_mission(
            description="Refactor main.py",
            target_repository=str(repo_dir),
        )
        mission_id = mission.id

        # Plan
        plan = plan_mission(description=mission.description, repo_path=str(repo_dir))
        controller.apply_plan(mission_id, plan["milestones"], plan.get("validation_contract"))

        # Start execution
        controller.start_execution(mission_id)

        # Cancel
        controller.cancel_mission(mission_id)
        mission = mission_storage.get_mission(mission_id)
        assert mission.status == MissionStatus.CANCELLED.value

        # Resume
        controller.resume_mission(mission_id)
        mission = mission_storage.get_mission(mission_id)
        assert mission.status == MissionStatus.PLANNING.value

    def test_mission_pause_and_resume(self, tmp_path):
        """Test mission pause and resume."""
        repo_dir = self._create_test_repo(tmp_path)

        mission = controller.create_mission(
            description="Pause test",
            target_repository=str(repo_dir),
        )
        mission_id = mission.id

        # Pause
        controller.pause_mission(mission_id)
        mission = mission_storage.get_mission(mission_id)
        assert mission.status == MissionStatus.PAUSED.value

        # Resume
        controller.resume_mission(mission_id)
        mission = mission_storage.get_mission(mission_id)
        assert mission.status == MissionStatus.PLANNING.value

    def test_mission_stats(self, tmp_path):
        """Verify mission statistics are tracked correctly."""
        repo_dir = self._create_test_repo(tmp_path)

        # Create multiple missions
        for i in range(3):
            controller.create_mission(
                description=f"Stats test mission {i}",
                target_repository=str(repo_dir),
            )

        stats = mission_storage.get_mission_stats()
        assert stats["total_missions"] >= 3
        assert stats["planning"] >= 3

    def test_repo_intelligence(self, tmp_path):
        """Test repository intelligence analysis."""
        repo_dir = self._create_test_repo(tmp_path)
        info = analyze_repository(str(repo_dir))
        assert info is not None

    def test_checkpoint_recovery(self, tmp_path):
        """Test that checkpoints allow recovery after restart."""
        repo_dir = self._create_test_repo(tmp_path)

        mission = controller.create_mission(
            description="Checkpoint test",
            target_repository=str(repo_dir),
        )
        mission_id = mission.id

        # Plan
        plan = plan_mission(description=mission.description, repo_path=str(repo_dir))
        controller.apply_plan(mission_id, plan["milestones"], plan.get("validation_contract"))

        # Start execution
        controller.start_execution(mission_id)

        # Verify checkpoint exists (saved by apply_plan)
        checkpoint = mission_storage.get_latest_checkpoint(mission_id)
        assert checkpoint is not None
        assert checkpoint.mission_id == mission_id

        # Simulate recovery by loading checkpoint
        checkpoints = mission_storage.list_checkpoints(mission_id)
        assert len(checkpoints) > 0
        recovered = checkpoints[0]
        assert recovered.mission_id == mission_id

    def test_completion_report(self, tmp_path):
        """Test that a completion report is generated."""
        repo_dir = self._create_test_repo(tmp_path)

        mission = controller.create_mission(
            description="Report test",
            target_repository=str(repo_dir),
        )
        mission_id = mission.id

        # Plan and execute
        plan = plan_mission(description=mission.description, repo_path=str(repo_dir))
        controller.apply_plan(mission_id, plan["milestones"], plan.get("validation_contract"))
        controller.start_execution(mission_id)

        mission = mission_storage.get_mission(mission_id)
        if mission.milestones:
            controller.complete_milestone(mission_id, mission.milestones[0].id)

        # Verify logs contain completion info
        logs = mission_storage.get_mission_logs(mission_id)
        log_messages = [log["message"] for log in logs]
        assert any("completed" in msg.lower() for msg in log_messages)
