"""Unit tests for mission model serialization and deserialization."""

import json
import sys
from pathlib import Path

# Add Greenie to path so hub.mission is importable
greenie_root = Path(__file__).resolve().parent.parent.parent / "Greenie"
if str(greenie_root) not in sys.path:
    sys.path.insert(0, str(greenie_root))

from hub.mission.models import (
    AutonomyLevel,
    FeatureRole,
    FeatureStatus,
    Mission,
    MissionCheckpoint,
    MissionFeature,
    MissionMilestone,
    MilestoneStatus,
    MissionStatus,
    ValidationContract,
    ValidationSeverity,
    ValidationResult,
)


class TestValidationContract:
    def test_to_dict(self):
        vc = ValidationContract(
            mission_id="mission-1",
            description="All tests pass",
            assertions=[{"type": "test", "command": "pytest"}],
            test_commands=["pytest"],
            check_paths=["src/"],
            max_severity=ValidationSeverity.MAJOR.value,
        )
        d = vc.to_dict()
        assert d["mission_id"] == "mission-1"
        assert d["description"] == "All tests pass"
        assert d["test_commands"] == ["pytest"]
        assert d["max_severity"] == "major"

    def test_from_dict(self):
        data = {
            "id": "vc-abc123",
            "mission_id": "mission-1",
            "description": "Build passes",
            "assertions": [],
            "test_commands": ["npm test"],
            "check_paths": [],
            "max_severity": "critical",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        vc = ValidationContract.from_dict(data)
        assert vc.id == "vc-abc123"
        assert vc.mission_id == "mission-1"
        assert vc.test_commands == ["npm test"]

    def test_round_trip(self):
        vc = ValidationContract(
            mission_id="mission-1",
            description="Round trip test",
            assertions=[{"key": "value"}],
            test_commands=["echo test"],
        )
        d = vc.to_dict()
        vc2 = ValidationContract.from_dict(d)
        assert vc2.id == vc.id
        assert vc2.mission_id == vc.mission_id
        assert vc2.description == vc.description
        assert vc2.assertions == vc.assertions


class TestValidationResult:
    def test_to_dict(self):
        vr = ValidationResult(
            mission_id="mission-1",
            severity=ValidationSeverity.CRITICAL.value,
            file_path="src/main.py",
            line_number=42,
            explanation="Unused import",
            suggested_correction="Remove the import",
        )
        d = vr.to_dict()
        assert d["severity"] == "critical"
        assert d["file_path"] == "src/main.py"
        assert d["line_number"] == 42
        assert d["verified"] is False

    def test_from_dict(self):
        data = {
            "id": "vr-xyz",
            "mission_id": "mission-1",
            "milestone_id": "ms-1",
            "severity": "blocker",
            "file_path": "test.py",
            "line_number": 10,
            "explanation": "Test failure",
            "suggested_correction": "Fix the test",
            "verified": True,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        vr = ValidationResult.from_dict(data)
        assert vr.severity == "blocker"
        assert vr.verified is True
        assert vr.milestone_id == "ms-1"

    def test_round_trip(self):
        vr = ValidationResult(
            mission_id="mission-1",
            severity=ValidationSeverity.MINOR.value,
            explanation="Style issue",
        )
        d = vr.to_dict()
        vr2 = ValidationResult.from_dict(d)
        assert vr2.id == vr.id
        assert vr2.severity == vr.severity
        assert vr2.explanation == vr.explanation


class TestMissionFeature:
    def test_to_dict(self):
        mf = MissionFeature(
            mission_id="mission-1",
            milestone_id="ms-1",
            name="Add login",
            description="Implement login page",
            role=FeatureRole.WORKER.value,
            status=FeatureStatus.RUNNING.value,
            depends_on=["feat-a"],
            order=1,
        )
        d = mf.to_dict()
        assert d["name"] == "Add login"
        assert d["role"] == "worker"
        assert d["status"] == "running"
        assert d["depends_on"] == ["feat-a"]

    def test_from_dict(self):
        data = {
            "id": "feat-abc",
            "mission_id": "mission-1",
            "milestone_id": "ms-1",
            "name": "Feature",
            "description": "",
            "role": "validator",
            "model_override": "gpt-4o",
            "status": "completed",
            "output": "Done",
            "error": "",
            "depends_on": [],
            "order": 0,
            "started_at": "2024-01-01T00:00:00+00:00",
            "completed_at": "2024-01-01T00:01:00+00:00",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        mf = MissionFeature.from_dict(data)
        assert mf.id == "feat-abc"
        assert mf.role == "validator"
        assert mf.model_override == "gpt-4o"

    def test_round_trip(self):
        mf = MissionFeature(
            mission_id="mission-1",
            milestone_id="ms-1",
            name="Test feature",
            depends_on=["a", "b"],
        )
        d = mf.to_dict()
        mf2 = MissionFeature.from_dict(d)
        assert mf2.name == mf.name
        assert mf2.depends_on == mf.depends_on


class TestMissionMilestone:
    def test_to_dict(self):
        features = [
            MissionFeature(name="F1", mission_id="m1", milestone_id="ms1"),
            MissionFeature(name="F2", mission_id="m1", milestone_id="ms1"),
        ]
        mm = MissionMilestone(
            mission_id="mission-1",
            name="Milestone 1",
            status=MilestoneStatus.EXECUTING.value,
            success_criteria=["Tests pass"],
            features=features,
            order=0,
        )
        d = mm.to_dict()
        assert d["name"] == "Milestone 1"
        assert d["status"] == "executing"
        assert len(d["features"]) == 2
        assert d["features"][0]["name"] == "F1"

    def test_from_dict(self):
        data = {
            "id": "ms-abc",
            "mission_id": "mission-1",
            "name": "Planning",
            "description": "Initial planning",
            "status": "planning",
            "success_criteria": ["Plan created"],
            "features": [
                {
                    "id": "feat-1",
                    "mission_id": "mission-1",
                    "milestone_id": "ms-abc",
                    "name": "Plan",
                    "description": "",
                    "role": "worker",
                    "model_override": None,
                    "status": "pending",
                    "output": "",
                    "error": "",
                    "depends_on": [],
                    "order": 0,
                    "started_at": None,
                    "completed_at": None,
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
            "order": 0,
            "started_at": None,
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        mm = MissionMilestone.from_dict(data)
        assert mm.id == "ms-abc"
        assert len(mm.features) == 1
        assert mm.features[0].name == "Plan"

    def test_round_trip(self):
        mm = MissionMilestone(
            mission_id="mission-1",
            name="M1",
            success_criteria=["A", "B"],
            features=[MissionFeature(name="F", mission_id="m1", milestone_id="ms1")],
        )
        d = mm.to_dict()
        mm2 = MissionMilestone.from_dict(d)
        assert mm2.id == mm.id
        assert mm2.success_criteria == mm.success_criteria
        assert len(mm2.features) == 1


class TestMissionCheckpoint:
    def test_to_dict(self):
        mc = MissionCheckpoint(
            mission_id="mission-1",
            state_json=json.dumps({"status": "executing"}),
            description="After milestone 1",
        )
        d = mc.to_dict()
        assert d["mission_id"] == "mission-1"
        assert d["description"] == "After milestone 1"

    def test_from_dict(self):
        data = {
            "id": "chk-1",
            "mission_id": "mission-1",
            "state_json": "{}",
            "description": "Checkpoint",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        mc = MissionCheckpoint.from_dict(data)
        assert mc.id == "chk-1"
        assert mc.mission_id == "mission-1"


class TestMission:
    def test_to_dict(self):
        m = Mission(
            description="Add feature X",
            target_repository="/path/to/repo",
            status=MissionStatus.PLANNING.value,
            orchestrator_model="gpt-4o",
            worker_model="gpt-4o-mini",
            validator_model="claude-3-sonnet",
            autonomy_level=AutonomyLevel.RESTRICTED.value,
            parallel_workers=True,
            tags=["feature", "test"],
        )
        d = m.to_dict()
        assert d["description"] == "Add feature X"
        assert d["target_repository"] == "/path/to/repo"
        assert d["orchestrator_model"] == "gpt-4o"
        assert d["parallel_workers"] is True
        assert d["tags"] == ["feature", "test"]

    def test_from_dict(self):
        data = {
            "id": "mission-abc",
            "description": "Test mission",
            "target_repository": "/repo",
            "status": "executing",
            "orchestrator_model": "gpt-4o",
            "worker_model": None,
            "validator_model": None,
            "autonomy_level": "full_autonomous",
            "milestones": [],
            "validation_contract": None,
            "artifacts": [],
            "error": "",
            "parallel_workers": False,
            "started_at": "2024-01-01T00:00:00+00:00",
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
            "created_by": "user1",
            "tags": [],
        }
        m = Mission.from_dict(data)
        assert m.id == "mission-abc"
        assert m.status == "executing"
        assert m.autonomy_level == "full_autonomous"
        assert m.created_by == "user1"

    def test_from_dict_with_validation_contract(self):
        data = {
            "id": "mission-abc",
            "description": "Test",
            "target_repository": "/repo",
            "status": "planning",
            "orchestrator_model": None,
            "worker_model": None,
            "validator_model": None,
            "autonomy_level": "supervised",
            "milestones": [],
            "validation_contract": {
                "id": "vc-1",
                "mission_id": "mission-abc",
                "description": "Tests pass",
                "assertions": [],
                "test_commands": ["pytest"],
                "check_paths": [],
                "max_severity": "major",
                "created_at": "2024-01-01T00:00:00+00:00",
            },
            "artifacts": [],
            "error": "",
            "parallel_workers": False,
            "started_at": None,
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
            "created_by": "",
            "tags": [],
        }
        m = Mission.from_dict(data)
        assert m.validation_contract is not None
        assert m.validation_contract.test_commands == ["pytest"]

    def test_round_trip_full(self):
        vc = ValidationContract(
            mission_id="mission-1",
            description="All tests pass",
            test_commands=["pytest"],
        )
        features = [
            MissionFeature(name="F1", mission_id="mission-1", milestone_id="ms-1"),
        ]
        milestones = [
            MissionMilestone(
                mission_id="mission-1",
                name="M1",
                features=features,
                success_criteria=["Done"],
            )
        ]
        m = Mission(
            description="Full mission",
            target_repository="/repo",
            milestones=milestones,
            validation_contract=vc,
            autonomy_level=AutonomyLevel.SUPERVISED.value,
            tags=["a", "b"],
        )
        d = m.to_dict()
        m2 = Mission.from_dict(d)
        assert m2.id == m.id
        assert m2.description == m.description
        assert len(m2.milestones) == 1
        assert m2.milestones[0].name == "M1"
        assert m2.validation_contract is not None
        assert m2.autonomy_level == AutonomyLevel.SUPERVISED.value
        assert m2.tags == ["a", "b"]


class TestEnums:
    def test_mission_status_values(self):
        assert MissionStatus.PLANNING.value == "planning"
        assert MissionStatus.EXECUTING.value == "executing"
        assert MissionStatus.COMPLETED.value == "completed"
        assert MissionStatus.FAILED.value == "failed"
        assert MissionStatus.CANCELLED.value == "cancelled"

    def test_milestone_status_values(self):
        assert MilestoneStatus.PLANNING.value == "planning"
        assert MilestoneStatus.COMPLETED.value == "completed"

    def test_feature_status_values(self):
        assert FeatureStatus.PENDING.value == "pending"
        assert FeatureStatus.RUNNING.value == "running"
        assert FeatureStatus.COMPLETED.value == "completed"

    def test_validation_severity_values(self):
        assert ValidationSeverity.BLOCKER.value == "blocker"
        assert ValidationSeverity.CRITICAL.value == "critical"
        assert ValidationSeverity.INFO.value == "info"

    def test_autonomy_level_values(self):
        assert AutonomyLevel.SUPERVISED.value == "supervised"
        assert AutonomyLevel.RESTRICTED.value == "restricted_autonomous"
        assert AutonomyLevel.FULL.value == "full_autonomous"
