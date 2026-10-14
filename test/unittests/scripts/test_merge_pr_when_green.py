import json
import subprocess
from collections.abc import Callable
from types import SimpleNamespace

import pytest

from scripts import merge_pr_when_green
from scripts.merge_pr_when_green import _commits_behind_base
from scripts.merge_pr_when_green import _failed_required_run_ids
from scripts.merge_pr_when_green import _rerun_failed_checks_once
from scripts.merge_pr_when_green import _update_branch_if_behind
from scripts.merge_pr_when_green import main

PR_URL = "https://github.com/dasch-swiss/dsp-tools/pull/2456"
REPO = "dasch-swiss/dsp-tools"
HEAD_SHA = "ff711d4269d1d0b38825a091a6004d779e65c735"
RUN_LINK = "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/1"
MERGE_CALL = ("pr", "merge", "--squash", "--admin", PR_URL)
UPDATE_CALL = ("pr", "update-branch", PR_URL)
# GitHub's merge error for a PR that is behind its base: it never says "behind" and lists its checks as "expected".
BEHIND_MERGE_ERROR = (
    "GraphQL: At least 1 approving review is required by reviewers with write access. "
    "13 of 13 required status checks are expected. (mergePullRequest)"
)

Handler = Callable[[tuple[str, ...]], subprocess.CompletedProcess[str]]


def _result(stdout: str = "", *, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr)


def _patch_gh(monkeypatch: pytest.MonkeyPatch, handler: Handler) -> list[tuple[str, ...]]:
    """Replaces the gh CLI by `handler`, and returns the list that records every call."""
    calls: list[tuple[str, ...]] = []

    def fake_gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        result = handler(args)
        if check:
            result.check_returncode()
        return result

    monkeypatch.setattr(merge_pr_when_green, "_gh", fake_gh)
    return calls


def _patch_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replaces the clock of the script by one that `sleep` advances at once."""
    now = [0.0]

    def sleep(seconds: float) -> None:
        now[0] += seconds

    def monotonic() -> float:
        return now[0]

    monkeypatch.setattr(merge_pr_when_green, "time", SimpleNamespace(monotonic=monotonic, sleep=sleep))


def _checks_json(*checks: tuple[str, str]) -> str:
    """Builds the output of `gh pr checks --json bucket,link` from (bucket, link) pairs."""
    return json.dumps([{"bucket": bucket, "link": link} for bucket, link in checks])


def _behind_handler(
    compare: subprocess.CompletedProcess[str], update: subprocess.CompletedProcess[str] | None = None
) -> Handler:
    """Answers the PR lookup, the compare call, and (if `update` is given) the branch update."""

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "view"):
                return _result(json.dumps({"baseRefName": "main", "headRefOid": HEAD_SHA}))
            case ("api", _):
                return compare
            case ("pr", "update-branch") if update is not None:
                return update
        raise AssertionError(args)

    return handler


def _rerun_handler(*, attempt: int, status: str, rerun_returncode: int = 0) -> Handler:
    """Plays one failed required check in run 111, whose latest attempt and status are given."""

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "checks"):
                return _result(_checks_json(("fail", RUN_LINK)), returncode=1)
            case ("run", "view"):
                return _result(json.dumps({"attempt": attempt, "status": status}))
            case ("run", "rerun"):
                return _result(returncode=rerun_returncode)
        raise AssertionError(args)

    return handler


def _loop_handler(
    merges: list[subprocess.CompletedProcess[str]], *, state: str = "OPEN", behind_by: int = 0
) -> Handler:
    """
    Plays a PR whose merge attempts get the results of `merges` in turn, the last result repeating.

    A branch update succeeds and brings the branch up to date.
    """
    attempts = list(merges)
    behind = [behind_by]

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "merge"):
                return attempts.pop(0) if len(attempts) > 1 else attempts[0]
            case ("pr", "view") if "state" in args:
                return _result(f"{state}\n")
            case ("pr", "view"):
                return _result(json.dumps({"baseRefName": "main", "headRefOid": HEAD_SHA}))
            case ("pr", "checks"):
                return _result(returncode=1, stderr="no required checks reported on the branch")
            case ("api", _):
                return _result(json.dumps({"behind_by": behind[0]}))
            case ("pr", "update-branch"):
                behind[0] = 0
                return _result()
        raise AssertionError(args)

    return handler


class TestFailedRequiredRunIds:
    def test_returns_each_failed_run_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stdout = _checks_json(
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/222/job/1"),
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/1"),
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/2"),
        )
        _patch_gh(monkeypatch, lambda _args: _result(stdout, returncode=1))
        assert _failed_required_run_ids(PR_URL) == ["111", "222"]

    def test_ignores_checks_that_did_not_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stdout = _checks_json(("pass", RUN_LINK), ("pending", RUN_LINK), ("skipping", RUN_LINK))
        _patch_gh(monkeypatch, lambda _args: _result(stdout, returncode=8))
        assert _failed_required_run_ids(PR_URL) == []

    def test_returns_nothing_when_gh_prints_no_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        no_checks = _result(returncode=1, stderr="no required checks reported on the 'chore/bump' branch")
        _patch_gh(monkeypatch, lambda _args: no_checks)
        assert _failed_required_run_ids(PR_URL) == []


class TestCommitsBehindBase:
    def test_asks_the_compare_api_with_the_base_name_and_the_head_sha(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": 2}))))
        assert _commits_behind_base(PR_URL, REPO) == 2
        assert ("api", f"repos/{REPO}/compare/main...{HEAD_SHA}") in calls


class TestUpdateBranchIfBehind:
    def test_updates_a_branch_that_is_behind(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": 2})), _result()))
        _update_branch_if_behind(PR_URL, REPO)
        assert UPDATE_CALL in calls
        assert "branch behind base by 2 commits" in capsys.readouterr().out

    def test_leaves_a_current_branch_alone(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": 0}))))
        _update_branch_if_behind(PR_URL, REPO)
        assert UPDATE_CALL not in calls

    def test_warns_when_the_update_fails(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        update_failure = _result(returncode=1, stderr="merge conflict between base and head")
        _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": 2})), update_failure))
        _update_branch_if_behind(PR_URL, REPO)
        out = capsys.readouterr().out
        assert "::warning::could not update the branch" in out
        assert "merge conflict between base and head" in out

    def test_warns_when_the_lookup_fails(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = _patch_gh(monkeypatch, _behind_handler(_result(returncode=1, stderr="HTTP 502")))
        _update_branch_if_behind(PR_URL, REPO)
        assert UPDATE_CALL not in calls
        out = capsys.readouterr().out
        assert "::warning::could not tell whether" in out
        assert "HTTP 502" in out


class TestRerunFailedChecksOnce:
    def test_reruns_a_failed_check_and_records_its_attempt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, _rerun_handler(attempt=1, status="completed"))
        before: dict[str, int] = {}
        assert _rerun_failed_checks_once(PR_URL, before) == {"111": 1}
        assert ("run", "rerun", "111", "--failed") in calls
        assert before == {}

    @pytest.mark.parametrize(("attempt", "status"), [(1, "completed"), (2, "in_progress")])
    def test_waits_for_the_rerun_to_finish(self, monkeypatch: pytest.MonkeyPatch, attempt: int, status: str) -> None:
        calls = _patch_gh(monkeypatch, _rerun_handler(attempt=attempt, status=status))
        assert _rerun_failed_checks_once(PR_URL, {"111": 1}) == {"111": 1}
        assert ("run", "rerun", "111", "--failed") not in calls

    def test_exits_when_the_rerun_failed_too(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _patch_gh(monkeypatch, _rerun_handler(attempt=2, status="completed"))
        with pytest.raises(SystemExit) as exit_info:
            _rerun_failed_checks_once(PR_URL, {"111": 1})
        assert exit_info.value.code == 1
        assert "not a flake" in capsys.readouterr().out

    def test_exits_when_the_rerun_cannot_start(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _patch_gh(monkeypatch, _rerun_handler(attempt=1, status="completed", rerun_returncode=1))
        with pytest.raises(SystemExit) as exit_info:
            _rerun_failed_checks_once(PR_URL, {})
        assert exit_info.value.code == 1
        assert "could not be re-run" in capsys.readouterr().out

    def test_does_nothing_when_no_check_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, lambda _args: _result(_checks_json(("pass", RUN_LINK))))
        assert _rerun_failed_checks_once(PR_URL, {}) == {}
        assert [call[:2] for call in calls] == [("pr", "checks")]


class TestMain:
    @pytest.fixture(autouse=True)
    def _setup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PR_URL", PR_URL)
        monkeypatch.setenv("TIMEOUT_MINUTES", "30")
        monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
        _patch_clock(monkeypatch)

    def test_merges_at_once_when_checks_are_green(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = _patch_gh(monkeypatch, _loop_handler([_result()]))
        main()
        assert calls == [MERGE_CALL]
        assert "::notice::merged" in capsys.readouterr().out

    def test_stops_when_someone_else_merged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        already_merged = _result(returncode=1, stderr="Pull request is already merged")
        calls = _patch_gh(monkeypatch, _loop_handler([already_merged], state="MERGED"))
        main()
        assert calls.count(MERGE_CALL) == 1
        assert UPDATE_CALL not in calls

    def test_updates_a_branch_that_fell_behind_main(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR), _result()]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=2))
        main()
        assert calls.count(UPDATE_CALL) == 1
        assert calls.count(MERGE_CALL) == 2
        assert "::notice::merged" in capsys.readouterr().out

    def test_exits_at_the_deadline(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setenv("TIMEOUT_MINUTES", "1")
        calls = _patch_gh(monkeypatch, _loop_handler([_result(returncode=1, stderr=BEHIND_MERGE_ERROR)]))
        with pytest.raises(SystemExit) as exit_info:
            main()
        assert exit_info.value.code == 1
        assert calls.count(MERGE_CALL) == 3
        assert "could not merge" in capsys.readouterr().out
