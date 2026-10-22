"""Unit tests for Phase 11 — Agent Harness components.

Tests for Spec Mode, Custom Droids, Skills, Hooks, and Environments.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add Greenie to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Greenie"))


class TestSpecMode:
    """Tests for Spec Mode."""

    def test_create_spec(self):
        """Test creating a new spec."""
        from hub.mission.spec_mode import create_spec, get_spec, delete_spec

        spec = create_spec(
            title="Add auth",
            description="Add user authentication",
            target_repository="/tmp/test-repo",
        )
        assert spec.id.startswith("spec-")
        assert spec.title == "Add auth"
        assert spec.status == "draft"

        retrieved = get_spec(spec.id)
        assert retrieved is not None
        assert retrieved.title == "Add auth"

        delete_spec(spec.id)

    def test_create_spec_validation(self):
        """Test spec creation validates required fields."""
        from hub.mission.spec_mode import create_spec

        try:
            create_spec(title="", description="test", target_repository="/tmp")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "title" in str(e)

        try:
            create_spec(title="Test", description="", target_repository="/tmp")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "description" in str(e)

    def test_research_spec(self):
        """Test research phase produces findings."""
        from hub.mission.spec_mode import create_spec, research_spec, delete_spec

        spec = create_spec(
            title="Test spec",
            description="Test description",
            target_repository=str(Path(__file__).parent.parent.parent),
        )

        researched = research_spec(spec.id)
        assert researched.status == "ready_for_review"
        assert len(researched.findings) > 0
        assert researched.proposal is not None

        delete_spec(spec.id)

    def test_approve_spec(self):
        """Test approving a spec."""
        from hub.mission.spec_mode import create_spec, research_spec, approve_spec, delete_spec

        spec = create_spec(
            title="Test",
            description="Test",
            target_repository=str(Path(__file__).parent.parent.parent),
        )
        research_spec(spec.id)
        approved = approve_spec(spec.id)
        assert approved.status == "approved"

        delete_spec(spec.id)

    def test_reject_spec(self):
        """Test rejecting a spec with feedback."""
        from hub.mission.spec_mode import create_spec, research_spec, reject_spec, delete_spec

        spec = create_spec(
            title="Test",
            description="Test",
            target_repository=str(Path(__file__).parent.parent.parent),
        )
        research_spec(spec.id)
        rejected = reject_spec(spec.id, "Needs more detail")
        assert rejected.status == "rejected"
        assert rejected.feedback == "Needs more detail"

        delete_spec(spec.id)

    def test_list_specs(self):
        """Test listing specs with filters."""
        from hub.mission.spec_mode import create_spec, list_specs, delete_spec

        spec1 = create_spec("Test 1", "Desc 1", "/tmp/repo1")
        spec2 = create_spec("Test 2", "Desc 2", "/tmp/repo2")

        all_specs = list_specs()
        assert len(all_specs) >= 2

        draft_specs = list_specs(status="draft")
        assert len(draft_specs) >= 2

        delete_spec(spec1.id)
        delete_spec(spec2.id)

    def test_spec_stats(self):
        """Test spec statistics."""
        from hub.mission.spec_mode import create_spec, research_spec, approve_spec, get_spec_stats, delete_spec

        spec = create_spec("Stats test", "Test", "/tmp/repo")
        stats = get_spec_stats()
        assert "total_specs" in stats
        assert stats["total_specs"] >= 1

        delete_spec(spec.id)

    def test_convert_spec_to_mission(self):
        """Test converting approved spec to mission."""
        from hub.mission.spec_mode import create_spec, research_spec, approve_spec, convert_spec_to_mission, delete_spec

        spec = create_spec(
            "Convert test",
            "Test conversion",
            str(Path(__file__).parent.parent.parent),
        )
        research_spec(spec.id)
        approve_spec(spec.id)
        mission = convert_spec_to_mission(spec.id)

        assert mission.id.startswith("mission-")
        assert "Convert test" in mission.description

        # Clean up mission
        from hub.mission import storage as mission_storage
        mission_storage.delete_mission(mission.id)
        delete_spec(spec.id)


class TestDroids:
    """Tests for Custom Droids."""

    def test_builtin_droids(self):
        """Test built-in droids are available."""
        from hub.mission.droids import BUILTIN_DROIDS, discover_droids

        assert "worker" in BUILTIN_DROIDS
        assert "explorer" in BUILTIN_DROIDS
        assert "reviewer" in BUILTIN_DROIDS
        assert "validator" in BUILTIN_DROIDS

        droids = discover_droids()
        names = [d.name for d in droids]
        assert "worker" in names

    def test_create_droid(self):
        """Test creating a custom droid."""
        from hub.mission.droids import create_droid, get_stored_droid, delete_stored_droid

        droid = create_droid(
            name="test-droid",
            description="A test droid",
            system_prompt="You are a test droid.",
            model="gpt-4o",
        )
        assert droid.name == "test-droid"
        assert droid.model == "gpt-4o"

        retrieved = get_stored_droid("test-droid")
        assert retrieved is not None
        assert retrieved.description == "A test droid"

        delete_stored_droid("test-droid")

    def test_create_droid_validation(self):
        """Test droid creation validates required fields."""
        from hub.mission.droids import create_droid

        try:
            create_droid(name="", description="test", system_prompt="test")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        try:
            create_droid(name="test", description="test", system_prompt="")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_create_droid_conflicts_builtin(self):
        """Test droid name conflicts with built-in."""
        from hub.mission.droids import create_droid

        try:
            create_droid(name="worker", description="test", system_prompt="test")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "built-in" in str(e).lower() or "conflict" in str(e).lower()

    def test_invoke_droid(self):
        """Test invoking a droid."""
        from hub.mission.droids import invoke_droid

        result = invoke_droid("worker", "Add a feature")
        assert result["droid"]["name"] == "worker"
        assert result["task"] == "Add a feature"

    def test_parse_droid_markdown(self):
        """Test parsing droid definition from markdown."""
        from hub.mission.droids import _parse_droid_markdown

        content = """---
name: my-droid
description: A custom droid
model: gpt-4o
allowed_tools: [read_file, write_file]
---
You are a custom droid.
"""
        droid = _parse_droid_markdown(content, "/path/to/my-droid.md")
        assert droid.name == "my-droid"
        assert droid.model == "gpt-4o"
        assert "read_file" in droid.allowed_tools

    def test_list_stored_droids(self):
        """Test listing stored droids."""
        from hub.mission.droids import create_droid, list_stored_droids, delete_stored_droid

        create_droid("list-test", "Test", "You are a test droid.")
        droids = list_stored_droids()
        names = [d.name for d in droids]
        assert "list-test" in names

        delete_stored_droid("list-test")


class TestSkills:
    """Tests for Skills System."""

    def test_create_skill(self):
        """Test creating a skill."""
        from hub.mission.skills import create_skill, get_stored_skill, delete_stored_skill

        skill = create_skill(
            name="test-skill",
            description="A test skill",
            instructions="Do something useful.",
            triggers=["deploy", "release"],
        )
        assert skill.name == "test-skill"
        assert "deploy" in skill.triggers

        retrieved = get_stored_skill("test-skill")
        assert retrieved is not None

        delete_stored_skill("test-skill")

    def test_create_skill_validation(self):
        """Test skill creation validates required fields."""
        from hub.mission.skills import create_skill

        try:
            create_skill(name="", description="test", instructions="test")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_match_skills(self):
        """Test matching skills to a task."""
        from hub.mission.skills import create_skill, match_skills, delete_stored_skill

        skill = create_skill(
            "match-test", "Test", "Instructions",
            triggers=["deploy", "release"],
        )
        matched = match_skills("I need to deploy the app")
        names = [s.name for s in matched]
        assert "match-test" in names

        delete_stored_skill("match-test")

    def test_invoke_skill(self):
        """Test invoking a skill."""
        from hub.mission.skills import create_skill, invoke_skill, delete_stored_skill

        skill = create_skill("invoke-test", "Test", "Instructions")
        result = invoke_skill("invoke-test", "Do the task")
        assert result["skill"]["name"] == "invoke-test"

        delete_stored_skill("invoke-test")

    def test_parse_skill_markdown(self):
        """Test parsing SKILL.md."""
        from hub.mission.skills import _parse_skill_markdown

        content = """---
name: my-skill
description: A skill
triggers: [deploy]
user_invocable: true
---
Instructions here.
"""
        skill = _parse_skill_markdown(content, "/path/to/skill")
        assert skill.name == "my-skill"
        assert skill.user_invocable is True


class TestHooks:
    """Tests for Hooks System."""

    def test_create_hook(self):
        """Test creating a hook."""
        from hub.mission.hooks import create_hook, get_hook, delete_hook

        hook = create_hook(
            name="test-hook",
            event="mission_start",
            hook_type="script",
            target="/bin/echo",
            description="A test hook",
        )
        assert hook.name == "test-hook"
        assert hook.event == "mission_start"

        retrieved = get_hook(hook.id)
        assert retrieved is not None

        delete_hook(hook.id)

    def test_create_hook_validation(self):
        """Test hook creation validates required fields."""
        from hub.mission.hooks import create_hook

        try:
            create_hook(name="", event="mission_start", hook_type="script", target="/bin/echo")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        try:
            create_hook(name="test", event="invalid_event", hook_type="script", target="/bin/echo")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_list_hooks(self):
        """Test listing hooks."""
        from hub.mission.hooks import create_hook, list_hooks, delete_hook

        hook = create_hook("list-test", "mission_start", "script", "/bin/echo")
        hooks = list_hooks(event="mission_start")
        ids = [h.id for h in hooks]
        assert hook.id in ids

        delete_hook(hook.id)

    def test_hook_events(self):
        """Test all hook event types."""
        from hub.mission.hooks import HookEvent

        events = [e.value for e in HookEvent]
        assert "pre_tool_use" in events
        assert "mission_start" in events
        assert "validation_fail" in events

    def test_delete_hook(self):
        """Test deleting a hook."""
        from hub.mission.hooks import create_hook, delete_hook

        hook = create_hook("delete-test", "mission_start", "script", "/bin/echo")
        deleted = delete_hook(hook.id)
        assert deleted is True

        deleted_again = delete_hook(hook.id)
        assert deleted_again is False


class TestEnvironments:
    """Tests for Environments."""

    def test_create_environment(self):
        """Test creating an environment."""
        from hub.mission.environments import create_environment, get_environment, delete_environment

        env = create_environment(
            name="test-env",
            repository="/tmp/test-repo",
            description="A test environment",
            python_version="3.12",
            test_command="pytest",
        )
        assert env.name == "test-env"
        assert env.python_version == "3.12"

        retrieved = get_environment(env.id)
        assert retrieved is not None

        delete_environment(env.id)

    def test_create_environment_validation(self):
        """Test environment creation validates required fields."""
        from hub.mission.environments import create_environment

        try:
            create_environment(name="", repository="/tmp")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_list_environments(self):
        """Test listing environments."""
        from hub.mission.environments import create_environment, list_environments, delete_environment

        env = create_environment("list-env", "/tmp/repo")
        envs = list_environments()
        ids = [e.id for e in envs]
        assert env.id in ids

        delete_environment(env.id)

    def test_validate_environment(self):
        """Test environment validation."""
        from hub.mission.environments import create_environment, validate_environment, delete_environment

        env = create_environment(
            "validate-env",
            str(Path(__file__).parent.parent.parent),
            health_check_command="echo ok",
        )
        result = validate_environment(env.id)
        assert "checks" in result
        assert "passed" in result

        delete_environment(env.id)

    def test_delete_environment(self):
        """Test deleting an environment."""
        from hub.mission.environments import create_environment, delete_environment

        env = create_environment("delete-env", "/tmp/repo")
        deleted = delete_environment(env.id)
        assert deleted is True

        deleted_again = delete_environment(env.id)
        assert deleted_again is False
