from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest

from scripts import test_all


@pytest.mark.parametrize("failure", [None, "sqlscope", "clone", "install"])
def test_fresh_dependency_suites_and_cleanup(monkeypatch, failure):
    calls = []
    checkouts = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        if command[0] == "git":
            path = Path(command[-1])
            checkouts.append(path)
            (path / "tests").mkdir(parents=True)
            if failure == "clone":
                raise subprocess.CalledProcessError(1, command)
        elif "pip" in command:
            assert all(path.is_dir() for path in checkouts)
            assert not any("-e" == arg for arg in command)
            if failure == "install":
                raise subprocess.CalledProcessError(1, command)
        else:
            assert kwargs["cwd"].is_dir()
            return SimpleNamespace(returncode=int(kwargs["cwd"].name == failure))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(test_all.subprocess, "run", run)
    monkeypatch.setattr(test_all.sys, "argv", ["test_all.py", "-q"])

    assert test_all.main() == int(failure is not None)
    assert checkouts
    assert all(not path.parent.exists() for path in checkouts)
    if failure in ("clone", "install"):
        assert not any("pytest" in command for command, _ in calls)
        return

    assert [path.name for path in checkouts] == list(test_all.PACKAGES)
    assert all(
        command[-2] == f"https://github.com/DavidePonzini/{path.name}.git"
        for (command, _), path in zip(calls, checkouts)
    )
    test_calls = [(command, kwargs) for command, kwargs in calls if "pytest" in command]
    assert test_calls == [
        ([test_all.sys.executable, "-m", "pytest", "tests", "-q"], {"cwd": path})
        for path in checkouts
    ]
