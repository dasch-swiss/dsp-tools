import subprocess
from pathlib import Path

import pytest

from scripts import bump_version
from scripts.bump_version import _calculate_new_version
from scripts.bump_version import _make_sys_call
from scripts.bump_version import _post_release_version
from scripts.bump_version import _write_new_version_into_pyproject_toml
from scripts.bump_version import main

DESCRIBE_CALL = "git describe --tags --abbrev=0 --match v[0-9]*"
BRANCH_CALL = "git rev-parse --abbrev-ref HEAD"
COUNT_CALL = "git rev-list --count main ^v9.0.2"

PYPROJECT = """\
[project]
name = "dsp-tools"
version = "9.0.2"  # keep this comment
description = "DSP-TOOLS"
"""


def _write_pyproject(repo_root: Path) -> Path:
    pyproject = repo_root / "packages" / "dsp-tools" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True)
    pyproject.write_text(PYPROJECT, encoding="utf-8")
    return pyproject


def _patch_sys_call(monkeypatch: pytest.MonkeyPatch, answers: dict[str, str]) -> list[str]:
    """Replaces `_make_sys_call` by a lookup in `answers`, and returns the list that records every call."""
    calls: list[str] = []

    def fake_sys_call(call: str) -> str:
        calls.append(call)
        return answers[call]

    monkeypatch.setattr(bump_version, "_make_sys_call", fake_sys_call)
    return calls


class TestMain:
    def test_writes_post_release_version(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path)
        monkeypatch.chdir(tmp_path)
        _patch_sys_call(monkeypatch, {DESCRIBE_CALL: "v9.0.2", BRANCH_CALL: "main", COUNT_CALL: "5"})
        main()
        expected = PYPROJECT.replace('version = "9.0.2"', 'version = "9.0.2.post4"')
        assert pyproject.read_text(encoding="utf-8") == expected

    def test_leaves_pyproject_unchanged_on_release_commit(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        pyproject = _write_pyproject(tmp_path)
        monkeypatch.chdir(tmp_path)
        _patch_sys_call(monkeypatch, {DESCRIBE_CALL: "v9.0.2", BRANCH_CALL: "main", COUNT_CALL: "0"})
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        assert pyproject.read_text(encoding="utf-8") == PYPROJECT


class TestPostReleaseVersion:
    def test_counts_post_releases_from_zero(self) -> None:
        assert _post_release_version("v9.0.2", 5) == "9.0.2.post4"

    def test_first_commit_after_release(self) -> None:
        assert _post_release_version("v9.0.2", 1) == "9.0.2.post0"

    def test_multi_digit_version(self) -> None:
        assert _post_release_version("v19.3.14", 12) == "19.3.14.post11"


class TestCalculateNewVersion:
    def test_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_sys_call(monkeypatch, {BRANCH_CALL: "main", COUNT_CALL: "5"})
        assert _calculate_new_version("v9.0.2") == "9.0.2.post4"
        assert calls == [BRANCH_CALL, COUNT_CALL]

    def test_raises_on_other_branch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_sys_call(monkeypatch, {BRANCH_CALL: "feature-branch"})
        with pytest.raises(ValueError, match="main branch"):
            _calculate_new_version("v9.0.2")
        assert calls == [BRANCH_CALL]

    def test_exits_without_error_on_release_commit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_sys_call(monkeypatch, {BRANCH_CALL: "main", COUNT_CALL: "0"})
        with pytest.raises(SystemExit) as exc_info:
            _calculate_new_version("v9.0.2")
        assert exc_info.value.code == 0


class TestWriteNewVersionIntoPyprojectToml:
    def test_replaces_version(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path)
        monkeypatch.chdir(tmp_path)
        _write_new_version_into_pyproject_toml(old_version="9.0.2", new_version="9.0.2.post4")
        expected = PYPROJECT.replace('version = "9.0.2"', 'version = "9.0.2.post4"')
        assert pyproject.read_text(encoding="utf-8") == expected

    def test_raises_on_version_mismatch(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path)
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match=r"9\.0\.1"):
            _write_new_version_into_pyproject_toml(old_version="9.0.1", new_version="9.0.1.post4")
        assert pyproject.read_text(encoding="utf-8") == PYPROJECT


class TestMakeSysCall:
    def test_returns_stdout_without_trailing_newline(self, monkeypatch: pytest.MonkeyPatch) -> None:
        received: list[tuple[list[str], dict[str, object]]] = []

        def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            received.append((args, kwargs))
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="v9.0.2\n")

        monkeypatch.setattr(subprocess, "run", fake_run)
        assert _make_sys_call(DESCRIBE_CALL) == "v9.0.2"
        [(args, kwargs)] = received
        assert args == ["git", "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"]
        assert kwargs["check"] is True

    def test_exits_with_error_when_call_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            raise subprocess.CalledProcessError(returncode=128, cmd=args, output="", stderr="fatal")

        monkeypatch.setattr(subprocess, "run", fake_run)
        with pytest.raises(SystemExit) as exc_info:
            _make_sys_call(DESCRIBE_CALL)
        assert exc_info.value.code == 1
