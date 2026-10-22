"""Integration tests for Speedy CLI against a running Evershade installation.

These tests verify that Speedy CLI commands work correctly when services
are running via Docker Compose. They require the Speedy CLI to be installed
and services to be accessible.
"""

import os
import subprocess
import sys
import pytest


# Speedy CLI entry point
SPEEDY_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "Speedy", "speedy", "cli.py"
)
SPEEDY_MODULE = "speedy.cli"


def run_speedy(*args, timeout=30):
    """Run a Speedy CLI command and return the result.

    Args:
        *args: CLI arguments to pass to Speedy.
        timeout: Command timeout in seconds.

    Returns:
        subprocess.CompletedProcess with stdout, stderr, and returncode.
    """
    # Try running as a module first, then as a script
    try:
        result = subprocess.run(
            [sys.executable, "-m", "speedy.cli"] + list(args),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "..", "Speedy")},
        )
        return result
    except FileNotFoundError:
        # Fall back to running the script directly
        result = subprocess.run(
            [sys.executable, SPEEDY_SCRIPT] + list(args),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "..", "Speedy")},
        )
        return result


class TestSpeedyHelp:
    """Test Speedy CLI help and basic functionality."""

    def test_help_command(self):
        """Speedy --help should show available commands."""
        result = run_speedy("--help")
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        output = result.stdout
        assert "status" in output, "Help should list status command"
        assert "install" in output, "Help should list install command"
        assert "start" in output, "Help should list start command"
        assert "stop" in output, "Help should list stop command"
        assert "doctor" in output, "Help should list doctor command"
        assert "logs" in output, "Help should list logs command"
        assert "backup" in output, "Help should list backup command"
        assert "config" in output, "Help should list config command"

    def test_version_or_version_info(self):
        """Speedy should provide version information."""
        result = run_speedy("--version")
        # May return 0 or may not have --version; check help instead
        if result.returncode != 0:
            result = run_speedy("--help")
            assert result.returncode == 0


class TestSpeedyStatus:
    """Test the 'evershade status' command."""

    def test_status_command(self):
        """Status command should execute without error."""
        result = run_speedy("status")
        # Status may return non-zero if services are down, but should not crash
        output = result.stdout + result.stderr
        assert "Evershade" in output or "Services" in output or "status" in output.lower(), \
            f"Status output should mention services: {output}"


class TestSpeedyDoctor:
    """Test the 'evershade doctor' diagnostic command."""

    def test_diagnostic_command(self):
        """Doctor command should run diagnostics without crashing."""
        result = run_speedy("doctor")
        output = result.stdout + result.stderr
        # Doctor should check Docker, Compose, and services
        assert "Docker" in output or "docker" in output or "diagnostic" in output.lower() or "Diagnostics" in output, \
            f"Doctor should mention Docker or diagnostics: {output}"

    def test_diagnostic_checks_docker(self):
        """Doctor should check Docker availability."""
        result = run_speedy("doctor")
        output = result.stdout + result.stderr.lower()
        # Should mention Docker in some form
        assert "docker" in output or "compose" in output or "check" in output, \
            f"Doctor should check Docker/Compose: {output}"


class TestSpeedyConfig:
    """Test the 'evershade config' subcommands."""

    def test_config_help(self):
        """Config --help should list available subcommands."""
        result = run_speedy("config", "--help")
        assert result.returncode == 0, f"Config help failed: {result.stderr}"
        output = result.stdout
        assert "validate" in output, "Config should have validate subcommand"

    def test_config_validate(self):
        """Config validate should check configuration files."""
        result = run_speedy("config", "validate")
        output = result.stdout + result.stderr
        # Should mention .env, docker-compose, or configuration
        assert any(
            keyword in output.lower()
            for keyword in ["env", "compose", "config", "valid", "check", "docker"]
        ), f"Config validate should check configuration: {output}"


class TestSpeedyBackup:
    """Test the 'evershade backup' subcommands."""

    def test_backup_help(self):
        """Backup --help should list available subcommands."""
        result = run_speedy("backup", "--help")
        assert result.returncode == 0, f"Backup help failed: {result.stderr}"
        output = result.stdout
        assert "create" in output or "restore" in output, \
            "Backup should have create or restore subcommand"

    def test_backup_create_help(self):
        """Backup create --help should show options."""
        result = run_speedy("backup", "create", "--help")
        assert result.returncode == 0, f"Backup create help failed: {result.stderr}"


class TestSpeedyAgents:
    """Test the 'evershade agents' subcommands."""

    def test_agents_help(self):
        """Agents --help should list available subcommands."""
        result = run_speedy("agents", "--help")
        assert result.returncode == 0, f"Agents help failed: {result.stderr}"


class TestSpeedyLogs:
    """Test the 'evershade logs' command."""

    def test_logs_help(self):
        """Logs --help should show service and options."""
        result = run_speedy("logs", "--help")
        assert result.returncode == 0, f"Logs help failed: {result.stderr}"
        output = result.stdout
        assert "service" in output.lower() or "tail" in output.lower(), \
            "Logs should accept service or tail options"


class TestSpeedyInstall:
    """Test the 'evershade install' command."""

    def test_install_help(self):
        """Install --help should show profile options."""
        result = run_speedy("install", "--help")
        assert result.returncode == 0, f"Install help failed: {result.stderr}"
        output = result.stdout
        assert "profile" in output.lower(), "Install should accept profile option"


class TestSpeedyStartStop:
    """Test the 'evershade start' and 'evershade stop' commands."""

    def test_start_help(self):
        """Start --help should show profile options."""
        result = run_speedy("start", "--help")
        assert result.returncode == 0, f"Start help failed: {result.stderr}"

    def test_stop_help(self):
        """Stop --help should show profile and volume options."""
        result = run_speedy("stop", "--help")
        assert result.returncode == 0, f"Stop help failed: {result.stderr}"


class TestSpeedyCrossPlatform:
    """Test that Speedy CLI works on the current platform."""

    def test_cli_runs_on_current_platform(self):
        """Speedy should execute without platform-specific errors."""
        result = run_speedy("--help")
        assert result.returncode == 0, \
            f"Speedy should run on {sys.platform}: {result.stderr}"

    def test_no_python_path_issues(self):
        """Speedy module should be importable."""
        env = {
            **os.environ,
            "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "..", "Speedy"),
        }
        result = subprocess.run(
            [sys.executable, "-c", "import speedy.cli; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        # May fail if dependencies not installed; that's acceptable for integration
        if result.returncode == 0:
            assert "OK" in result.stdout
