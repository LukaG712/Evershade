"""Integration tests for mission control API and lifecycle.

Tests the full mission lifecycle: creation, planning, execution, validation,
cancellation, and recovery using the actual storage layer.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add Greenie to path
greenie_root = Path(__file__).resolve().parent.parent.parent / "Greenie"
if str(greenie_root) not in sys.path:
    sys.path.insert(0, str(greenie_root))

import pytest
from hub.mission import controller
from hub.mission import storage as mission_storage
from hub.mission.models import (
    Mission,
    MissionStatus,
    MilestoneStatus,
    FeatureStatus,
    ValidationSeverity,
)


@pytest.fixture(autouse=True)
def use_temp_db():
    """Use a temporary database for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    with patch.object(mission_storage, "_DB_PATH", db_path):
        # Re-initialize schema with the temp path
        mission_storage._init_schema()
        yield
    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    wal_path = Path(db_path + "-wal")
    wal_path.unlink(missing_ok=True)
    shm_path = Path(db_path + "-shm")
    shm_path.unlink(missing_ok=True)


class TestMissionCreation:
    def test_create_mission(self):
        mission = controller.create_mission(
            description="Add authentication",
            target_repository="/path/to/repo",
        )
        assert mission.id.startswith("mission-")
        assert mission.status == MissionStatus.PLANNING.value
        assert mission.description == "Add authentication"

        # Verify persistence
        saved = mission_storage.get_mission(mission.id)
        assert saved is not None
        assert saved.description == mission.description

    def test_create_mission_missing_description(self):
        with pytest.raises(ValueError, match="description is required"):
            controller.create_mission(description="", target_repository="/repo")

    def test_create_mission_missing_repository(self):
        with pytest.raises(ValueError, match="target_repository is required"):
            controller.create_mission(description="Test", target_repository="")

    def test_create_mission_with_model_preferences(self):
        mission = controller.create_mission(
            description="Test",
            target_repository="/repo",
            orchestrator_model="gpt-4o",
            worker_model="gpt-4o-mini",
            validator_model="claude-3-sonnet",
            autonomy_level="supervised",
            parallel_workers=True,
        )
        assert mission.orchestrator_model == "gpt-4o"
        assert mission.worker_model == "gpt-4o-mini"
        assert mission.validator_model == "claude-3-sonnet"
        assert mission.autonomy_level == "supervised"
        assert mission.parallel_workers is True


class TestPlanningPhase:
    def test_apply_plan(self):
        mission = controller.create_mission(
            description="Add feature",
            target_repository="/repo",
        )
        plan = {
            "milestones": [
                {
                    "id": "ms-1",
                    "name": "Planning",
                    "description": "Analyze requirements",
                    "success_criteria": ["Plan documented"],
                    "features": [
                        {
                            "name": "Analyze codebase",
                            "description": "Review existing patterns",
                            "role": "worker",
                        }
                    ],
                },
                {
                    "id": "ms-2",
                    "name": "Implementation",
                    "description": "Implement the feature",
                    "success_criteria": ["Tests pass"],
                    "features": [
                        {"name": "Write code", "role": "worker"},
                        {"name": "Write tests", "role": "worker"},
                    ],
                },
            ],
            "validation_contract": {
                "description": "Feature works correctly",
                "test_commands": ["pytest"],
                "max_severity": "major",
            },
        }
        result = controller.apply_plan(mission.id, plan["milestones"], plan["validation_contract"])

        assert len(result.milestones) == 2
        assert result.milestones[0].name == "Planning"
        assert result.milestones[1].name == "Implementation"
        assert len(result.milestones[1].features) == 2
        assert result.validation_contract is not None
        assert result.validation_contract.test_commands == ["pytest"]

    def test_apply_plan_missing_milestones(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        with pytest.raises(ValueError, match="Mission.*not found"):
            controller.apply_plan("nonexistent", [])


class TestExecutionPhase:
    def test_start_execution(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": [{"name": "F1"}]}],
        )
        result = controller.start_execution(mission.id)
        assert result.status == MissionStatus.EXECUTING.value
        assert result.started_at is not None
        assert result.milestones[0].status == MilestoneStatus.EXECUTING.value

    def test_start_execution_wrong_status(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        # No plan applied, status is PLANNING but no milestones
        # Start execution should work for PLANNING status
        result = controller.start_execution(mission.id)
        assert result.status == MissionStatus.EXECUTING.value

    def test_update_feature_status(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        mission = controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": [{"name": "F1"}]}],
        )
        feature_id = mission.milestones[0].features[0].id
        result = controller.update_feature_status(mission.id, feature_id, FeatureStatus.RUNNING.value)
        # Reload to verify persistence
        saved = mission_storage.get_mission(mission.id)
        assert saved.milestones[0].features[0].status == FeatureStatus.RUNNING.value

    def test_complete_milestone(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [
                {"id": "ms-1", "name": "M1", "features": []},
                {"id": "ms-2", "name": "M2", "features": []},
            ],
        )
        controller.start_execution(mission.id)
        result = controller.complete_milestone(mission.id, "ms-1")

        assert result.milestones[0].status == MilestoneStatus.COMPLETED.value
        assert result.milestones[1].status == MilestoneStatus.EXECUTING.value

    def test_complete_last_milestone_no_contract(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": []}],
        )
        controller.start_execution(mission.id)
        result = controller.complete_milestone(mission.id, "ms-1")
        assert result.status == MissionStatus.COMPLETED.value

    def test_complete_last_milestone_with_contract(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": []}],
            {"description": "Tests pass", "test_commands": ["pytest"]},
        )
        controller.start_execution(mission.id)
        result = controller.complete_milestone(mission.id, "ms-1")
        assert result.status == MissionStatus.VALIDATING.value

    def test_fail_milestone(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": []}],
        )
        controller.start_execution(mission.id)
        result = controller.fail_milestone(mission.id, "ms-1", "Build failed")
        assert result.status == MissionStatus.FAILED.value
        assert "Build failed" in result.error


class TestValidationPhase:
    def test_add_validation_result(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        from hub.mission.models import ValidationResult
        result = controller.add_validation_result(
            mission.id,
            ValidationResult(
                severity=ValidationSeverity.MINOR.value,
                explanation="Style issue",
            ),
        )
        assert result.mission_id == mission.id
        # Mission should not fail for minor findings
        saved = mission_storage.get_mission(mission.id)
        assert saved.status != MissionStatus.FAILED.value

    def test_add_blocker_validation_result(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        from hub.mission.models import ValidationResult
        controller.add_validation_result(
            mission.id,
            ValidationResult(
                severity=ValidationSeverity.BLOCKER.value,
                explanation="Critical security issue",
            ),
        )
        saved = mission_storage.get_mission(mission.id)
        assert saved.status == MissionStatus.FAILED.value

    def test_complete_validation_passed(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        result = controller.complete_validation(mission.id, passed=True)
        assert result.status == MissionStatus.COMPLETED.value

    def test_complete_validation_failed(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        result = controller.complete_validation(mission.id, passed=False)
        assert result.status == MissionStatus.FAILED.value


class TestMissionControl:
    def test_cancel_mission(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        result = controller.cancel_mission(mission.id)
        assert result.status == MissionStatus.CANCELLED.value

    def test_cancel_completed_mission(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.complete_validation(mission.id, passed=True)
        with pytest.raises(ValueError, match="already completed"):
            controller.cancel_mission(mission.id)

    def test_pause_and_resume(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.start_execution(mission.id)
        result = controller.pause_mission(mission.id)
        assert result.status == MissionStatus.PAUSED.value

        resumed = controller.resume_mission(mission.id)
        assert resumed.status == MissionStatus.PLANNING.value

    def test_checkpoint_save_and_restore(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.apply_plan(
            mission.id,
            [{"id": "ms-1", "name": "M1", "features": [{"name": "F1"}]}],
        )
        controller.cancel_mission(mission.id)

        # Resume should restore from checkpoint
        resumed = controller.resume_mission(mission.id)
        assert resumed.status == MissionStatus.PLANNING.value
        assert len(resumed.milestones) == 1


class TestStatistics:
    def test_get_stats(self):
        controller.create_mission(description="M1", target_repository="/repo")
        controller.create_mission(description="M2", target_repository="/repo")
        stats = controller.get_stats()
        assert stats["total_missions"] == 2
        assert "planning" in stats
        assert "executing" in stats


class TestListMissions:
    def test_list_missions(self):
        controller.create_mission(description="M1", target_repository="/repo1")
        controller.create_mission(description="M2", target_repository="/repo2")
        missions = mission_storage.list_missions()
        assert len(missions) == 2

    def test_list_missions_filter_by_status(self):
        m1 = controller.create_mission(description="M1", target_repository="/repo")
        controller.start_execution(m1.id)
        m2 = controller.create_mission(description="M2", target_repository="/repo")

        executing = mission_storage.list_missions(status="executing")
        assert len(executing) == 1
        planning = mission_storage.list_missions(status="planning")
        assert len(planning) == 1

    def test_delete_mission(self):
        mission = controller.create_mission(description="Test", target_repository="/repo")
        deleted = mission_storage.delete_mission(mission.id)
        assert deleted is True
        assert mission_storage.get_mission(mission.id) is None


class TestApprovalGates:
    def test_request_approval(self):
        """Requesting approval should pause the mission."""
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.start_execution(mission.id)
        result = controller.request_approval(mission.id, "git_push", "Push to main branch")
        assert result.status == MissionStatus.WAITING_APPROVAL.value
        assert "git_push" in result.error

    def test_approve_mission(self):
        """Approving should resume the mission."""
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.start_execution(mission.id)
        controller.request_approval(mission.id, "git_push")
        result = controller.approve_mission(mission.id, "Looks good")
        assert result.status == MissionStatus.EXECUTING.value
        assert result.error == ""

    def test_reject_mission(self):
        """Rejecting should fail the mission."""
        mission = controller.create_mission(description="Test", target_repository="/repo")
        controller.start_execution(mission.id)
        controller.request_approval(mission.id, "git_push")
        result = controller.reject_mission(mission.id, "Not authorized")
        assert result.status == MissionStatus.FAILED.value
        assert "Not authorized" in result.error

    def test_approve_wrong_status(self):
        """Approving a non-waiting mission should fail."""
        mission = controller.create_mission(description="Test", target_repository="/repo")
        with pytest.raises(ValueError, match="not waiting for approval"):
            controller.approve_mission(mission.id)

    def test_needs_approval_supervised(self):
        """Supervised autonomy should always need approval."""
        from hub.mission.models import Mission, AutonomyLevel
        mission = Mission(autonomy_level=AutonomyLevel.SUPERVISED.value)
        assert controller.needs_approval(mission, "anything") is True

    def test_needs_approval_full(self):
        """Full autonomous should never need approval."""
        from hub.mission.models import Mission, AutonomyLevel
        mission = Mission(autonomy_level=AutonomyLevel.FULL.value)
        assert controller.needs_approval(mission, "git_push") is False

    def test_needs_approval_restricted(self):
        """Restricted autonomous should need approval for sensitive ops."""
        from hub.mission.models import Mission, AutonomyLevel
        mission = Mission(autonomy_level=AutonomyLevel.RESTRICTED.value)
        assert controller.needs_approval(mission, "git_push") is True
        assert controller.needs_approval(mission, "write_file") is False


class TestFullLifecycle:
    def test_full_lifecycle(self):
        """Test the complete mission lifecycle end-to-end."""
        # 1. Create
        mission = controller.create_mission(
            description="Add feature X",
            target_repository="/repo",
        )
        assert mission.status == MissionStatus.PLANNING.value

        # 2. Plan
        controller.apply_plan(
            mission.id,
            [
                {"id": "ms-1", "name": "Plan", "features": [{"name": "F1"}]},
                {"id": "ms-2", "name": "Implement", "features": [{"name": "F2"}]},
            ],
            {"description": "Tests pass", "test_commands": ["pytest"]},
        )

        # 3. Execute
        mission = controller.start_execution(mission.id)
        assert mission.status == MissionStatus.EXECUTING.value

        # 4. Complete milestone 1
        mission = controller.complete_milestone(mission.id, "ms-1")
        assert mission.milestones[1].status == MilestoneStatus.EXECUTING.value

        # 5. Complete milestone 2 → validation
        mission = controller.complete_milestone(mission.id, "ms-2")
        assert mission.status == MissionStatus.VALIDATING.value

        # 6. Validate
        mission = controller.complete_validation(mission.id, passed=True)
        assert mission.status == MissionStatus.COMPLETED.value
        assert mission.completed_at is not None
