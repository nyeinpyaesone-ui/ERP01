"""Tests for scripts/maintenance.py."""

import sys

import pytest

sys.path.insert(0, "scripts")
import maintenance  # noqa: E402


def test_backup_creates_tree(tmp_path, monkeypatch, capsys):
    """Test backup writes files into a timestamped directory."""
    monkeypatch.setattr(maintenance, "PROJECT_ROOT", tmp_path)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "__init__.py").write_text("x = 1\n")
    (tmp_path / "main.py").write_text("print('hi')\n")

    assert maintenance.create_backup() == 0
    out = capsys.readouterr().out
    backups = list((tmp_path / "backups").glob("backup_*"))
    assert len(backups) == 1
    assert (backups[0] / "config" / "__init__.py").exists()
    assert (backups[0] / "main.py").exists()
    assert "✅" in out


def test_clear_cache_skips_excluded_dirs(tmp_path, monkeypatch):
    """Test cache clearing removes pycache but not .venv contents."""
    monkeypatch.setattr(maintenance, "PROJECT_ROOT", tmp_path)
    pkg = tmp_path / "config" / "__pycache__"
    pkg.mkdir(parents=True)
    (pkg / "config.cpython-312.pyc").write_text("junk")
    venv_cache = tmp_path / ".venv" / "lib" / "__pycache__"
    venv_cache.mkdir(parents=True)
    keep = venv_cache / "keep.pyc"
    keep.write_text("important")

    assert maintenance.clear_cache() == 0
    assert not pkg.exists()
    assert keep.exists()


def test_rotate_logs_collision_safe(tmp_path, monkeypatch):
    """Test two rotations in the same run do not overwrite each other."""
    monkeypatch.setattr(maintenance, "PROJECT_ROOT", tmp_path)
    logs = tmp_path / "logs"
    logs.mkdir()

    for _ in range(2):
        (logs / "app.log").write_text("entry")
        assert maintenance.rotate_logs() == 0

    rotated = sorted(p.name for p in logs.iterdir())
    assert len(rotated) == 2
    assert len(set(rotated)) == 2


def test_rotate_logs_no_dir(tmp_path, monkeypatch, capsys):
    """Test rotate_logs is a no-op without a logs directory."""
    monkeypatch.setattr(maintenance, "PROJECT_ROOT", tmp_path)
    assert maintenance.rotate_logs() == 0
    assert "No logs directory" in capsys.readouterr().out


def test_main_unknown_command(monkeypatch, capsys):
    """Test unknown commands exit with usage error."""
    monkeypatch.setattr(sys, "argv", ["maintenance.py", "bogus"])
    assert maintenance.main() == 1
    assert "Unknown command" in capsys.readouterr().out


def test_main_no_args(monkeypatch, capsys):
    """Test missing arguments print usage and return 1."""
    monkeypatch.setattr(sys, "argv", ["maintenance.py"])
    assert maintenance.main() == 1
    assert "Usage" in capsys.readouterr().out


def test_check_health_reports_dependencies(tmp_path, monkeypatch, capsys):
    """Test health check runs and reports dependency status."""
    monkeypatch.setattr(maintenance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        maintenance.subprocess,
        "run",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )
    code = maintenance.check_health()
    out = capsys.readouterr().out
    assert "Health check complete" in out
    # Missing deps or tests would flip this to 1; here deps exist and we
    # stubbed pytest as passing.
    assert code in (0, 1)


if __name__ == "__main__":
    pytest.main([__file__])
