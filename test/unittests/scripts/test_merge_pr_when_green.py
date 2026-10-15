import json
import os
import subprocess
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import merge_pr_when_green
from scripts.merge_pr_when_green import MAX_FAILED_UPDATES
from scripts.merge_pr_when_green import _commits_behind_base
from scripts.merge_pr_when_green import _failed_required_run_ids
from scripts.merge_pr_when_green import _gh
from scripts.merge_pr_when_green import _is_behind_base
from scripts.merge_pr_when_green import _is_merged
from scripts.merge_pr_when_green import _require_env
from scripts.merge_pr_when_green import _rerun_failed_checks_once
from scripts.merge_pr_when_green import _update_branch
from scripts.merge_pr_when_green import main

PR_URL = "https://github.com/dasch-swiss/dsp-tools/pull/2456"
REPO = "dasch-swiss/dsp-tools"
HEAD_SHA = "ff711d4269d1d0b38825a091a6004d779e65c735"
RUN_LINK = "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/1"
MERGE_CALL = ("pr", "merge", "--squash", "--admin", PR_URL)
STATE_CALL = ("pr", "view", PR_URL, "--json", "state", "--jq", ".state")
UPDATE_CALL = ("pr", "update-branch", PR_URL)
CHECKS_CALL = ("pr", "checks", PR_URL, "--required", "--json", "bucket,link")
RUN_VIEW_CALL = ("run", "view", "111", "--json", "attempt,status")
RERUN_CALL = ("run", "rerun", "111", "--failed")
# Merge error of this PR while it was behind main, copied from the log of
# https://github.com/dasch-swiss/dsp-tools/actions/runs/38522748201 (2026-10-14).
# It never says "behind" and lists the checks as "expected".
BEHIND_MERGE_ERROR = (
    "GraphQL: At least 1 approving review is required by reviewers with write access. "
    "13 of 13 required status checks are expected. (mergePullRequest)"
)
# A fake gh that gets more calls than this stands for a loop that does not stop.
MAX_FAKE_CALLS = 500

Handler = Callable[[tuple[str, ...]], subprocess.CompletedProcess[str]]


def _result(stdout: str = "", *, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr)


def _patch_gh(monkeypatch: pytest.MonkeyPatch, handler: Handler) -> list[tuple[str, ...]]:
    """Replaces the gh CLI by `handler`, and returns the list that records every call."""
    calls: list[tuple[str, ...]] = []

    def fake_gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        assert len(calls) <= MAX_FAKE_CALLS
        result = handler(args)
        if check:
            result.check_returncode()
        return result

    monkeypatch.setattr(merge_pr_when_green, "_gh", fake_gh)
    return calls


def _patch_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replaces the clock of the script by one that `sleep` advances at once."""
    now = 0.0

    def sleep(seconds: float) -> None:
        nonlocal now
        now += seconds

    def monotonic() -> float:
        return now

    monkeypatch.setattr(merge_pr_when_green, "time", SimpleNamespace(monotonic=monotonic, sleep=sleep))


def _checks_json(*checks: tuple[str, str]) -> str:
    """Builds the output of `gh pr checks --json bucket,link` from (bucket, link) pairs."""
    return json.dumps([{"bucket": bucket, "link": link} for bucket, link in checks])


def _pr_lookup() -> subprocess.CompletedProcess[str]:
    return _result(json.dumps({"baseRefName": "main", "headRefOid": HEAD_SHA}))


def _behind_handler(compare: subprocess.CompletedProcess[str]) -> Handler:
    """Answers the PR lookup and the compare call."""

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "view"):
                return _pr_lookup()
            case ("api", _):
                return compare
        raise AssertionError(args)

    return handler


def _rerun_handler(*, attempt: int, status: str, rerun_returncode: int = 0, rerun_stderr: str = "") -> Handler:
    """Plays one failed required check in run 111, whose latest attempt and status are given."""

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "checks"):
                return _result(_checks_json(("fail", RUN_LINK)), returncode=1)
            case ("run", "view"):
                return _result(json.dumps({"attempt": attempt, "status": status}))
            case ("run", "rerun"):
                return _result(returncode=rerun_returncode, stderr=rerun_stderr)
        raise AssertionError(args)

    return handler


def _loop_handler(
    merges: list[subprocess.CompletedProcess[str]],
    *,
    state: str = "OPEN",
    behind_by: Sequence[int] = (0,),
    update: subprocess.CompletedProcess[str] | None = None,
) -> Handler:
    """
    Plays a PR whose merge attempts get the results of `merges` in turn, the last result repeating.

    The compare calls get the values of `behind_by` in turn, the last value repeating.
    A branch update gets the result `update`. Without it, the update succeeds and brings the branch up to date.
    """
    attempts = list(merges)
    behind = list(behind_by)

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        match args[:2]:
            case ("pr", "merge"):
                return attempts.pop(0) if len(attempts) > 1 else attempts[0]
            case ("pr", "view"):
                return _result(f"{state}\n") if "state" in args else _pr_lookup()
            case ("pr", "checks"):
                return _result(returncode=1, stderr="no required checks reported on the branch")
            case ("api", _):
                return _result(json.dumps({"behind_by": behind.pop(0) if len(behind) > 1 else behind[0]}))
            case ("pr", "update-branch"):
                if update is not None:
                    return update
                behind[:] = [0]
                return _result()
        raise AssertionError(args)

    return handler


def _with_failed_check(inner: Handler) -> Handler:
    """
    Adds one failed required check in run 111 to the PR that `inner` plays.

    A re-run of the run starts its next attempt, which is complete at once.
    """
    attempt = 1

    def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        nonlocal attempt
        match args[:2]:
            case ("pr", "checks"):
                return _result(_checks_json(("fail", RUN_LINK)), returncode=1)
            case ("run", "view"):
                return _result(json.dumps({"attempt": attempt, "status": "completed"}))
            case ("run", "rerun"):
                attempt += 1
                return _result()
        return inner(args)

    return handler


class TestRequireEnv:
    def test_returns_the_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MERGE_TEST_VARIABLE", "value")
        assert _require_env("MERGE_TEST_VARIABLE") == "value"

    @pytest.mark.parametrize("value", [None, ""])
    def test_exits_when_the_variable_is_missing_or_empty(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], value: str | None
    ) -> None:
        if value is None:
            monkeypatch.delenv("MERGE_TEST_VARIABLE", raising=False)
        else:
            monkeypatch.setenv("MERGE_TEST_VARIABLE", value)
        with pytest.raises(SystemExit) as exit_info:
            _require_env("MERGE_TEST_VARIABLE")
        assert exit_info.value.code == 1
        assert "MERGE_TEST_VARIABLE" in capsys.readouterr().out


class TestGh:
    @pytest.fixture(autouse=True)
    def _stub_gh(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        stub = tmp_path / "gh"
        stub.write_text('#!/bin/sh\necho "args: $*"\necho "reason" >&2\nexit "${GH_STUB_EXIT:-0}"\n')
        stub.chmod(0o755)
        monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")

    def test_returns_the_output_as_text(self) -> None:
        result = _gh("pr", "view")
        assert result.stdout == "args: pr view\n"
        assert result.stderr == "reason\n"

    def test_raises_when_gh_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GH_STUB_EXIT", "1")
        with pytest.raises(subprocess.CalledProcessError):
            _gh("pr", "view")

    def test_returns_the_failure_when_check_is_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GH_STUB_EXIT", "1")
        assert _gh("pr", "view", check=False).returncode == 1


class TestIsMerged:
    @pytest.mark.parametrize(("state", "expected"), [("MERGED", True), ("OPEN", False)])
    def test_reads_the_state_of_the_pr(self, monkeypatch: pytest.MonkeyPatch, state: str, expected: bool) -> None:
        calls = _patch_gh(monkeypatch, lambda _args: _result(f"{state}\n"))
        assert _is_merged(PR_URL) is expected
        assert calls == [STATE_CALL]


class TestFailedRequiredRunIds:
    def test_returns_each_failed_run_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stdout = _checks_json(
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/222/job/1"),
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/1"),
            ("fail", "https://github.com/dasch-swiss/dsp-tools/actions/runs/111/job/2"),
        )
        calls = _patch_gh(monkeypatch, lambda _args: _result(stdout, returncode=1))
        assert _failed_required_run_ids(PR_URL) == ["111", "222"]
        assert calls == [CHECKS_CALL]

    @pytest.mark.parametrize("bucket", ["fail", "cancel"])
    def test_returns_the_run_of_a_check_that_ended_without_passing(
        self, monkeypatch: pytest.MonkeyPatch, bucket: str
    ) -> None:
        _patch_gh(monkeypatch, lambda _args: _result(_checks_json((bucket, RUN_LINK)), returncode=1))
        assert _failed_required_run_ids(PR_URL) == ["111"]

    def test_ignores_checks_that_did_not_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stdout = _checks_json(("pass", RUN_LINK), ("pending", RUN_LINK), ("skipping", RUN_LINK))
        _patch_gh(monkeypatch, lambda _args: _result(stdout, returncode=8))
        assert _failed_required_run_ids(PR_URL) == []

    def test_returns_nothing_when_gh_prints_no_json(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        no_checks = _result(returncode=1, stderr="no required checks reported on the 'chore/bump' branch")
        _patch_gh(monkeypatch, lambda _args: no_checks)
        assert _failed_required_run_ids(PR_URL) == []
        assert "no required checks reported on the 'chore/bump' branch" in capsys.readouterr().out


class TestCommitsBehindBase:
    def test_asks_the_compare_api_with_the_base_name_and_the_head_sha(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": 2}))))
        assert _commits_behind_base(PR_URL, REPO) == 2
        assert ("pr", "view", PR_URL, "--json", "baseRefName,headRefOid") in calls
        assert ("api", f"repos/{REPO}/compare/main...{HEAD_SHA}") in calls


class TestIsBehindBase:
    @pytest.mark.parametrize(("behind_by", "expected"), [(0, False), (1, True), (2, True)])
    def test_reads_whether_the_branch_lacks_a_commit(
        self, monkeypatch: pytest.MonkeyPatch, behind_by: int, expected: bool
    ) -> None:
        _patch_gh(monkeypatch, _behind_handler(_result(json.dumps({"behind_by": behind_by}))))
        assert _is_behind_base(PR_URL, REPO) is expected

    def test_is_not_behind_when_the_lookup_fails(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _patch_gh(monkeypatch, _behind_handler(_result(returncode=1, stderr="HTTP 502")))
        assert _is_behind_base(PR_URL, REPO) is False
        out = capsys.readouterr().out
        assert "::warning::could not tell whether" in out
        assert "HTTP 502" in out

    @pytest.mark.parametrize("body", ["", "<html>", "{}", "null"])
    def test_is_not_behind_when_the_answer_is_unexpected(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], body: str
    ) -> None:
        _patch_gh(monkeypatch, _behind_handler(_result(body)))
        assert _is_behind_base(PR_URL, REPO) is False
        assert "::warning::could not tell whether" in capsys.readouterr().out


class TestUpdateBranch:
    def test_updates_the_branch_and_clears_the_failure_count(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = _patch_gh(monkeypatch, lambda _args: _result())
        assert _update_branch(PR_URL, 2) == 0
        assert calls == [UPDATE_CALL]
        assert f"::notice::updating the branch of {PR_URL}" in capsys.readouterr().out

    def test_counts_a_failed_update(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        update_failure = _result(returncode=1, stderr="merge conflict between base and head")
        _patch_gh(monkeypatch, lambda _args: update_failure)
        assert _update_branch(PR_URL, 1) == 2
        out = capsys.readouterr().out
        assert "::warning::could not update the branch" in out
        assert "merge conflict between base and head" in out

    def test_exits_at_the_last_failed_update_in_a_row(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        update_failure = _result(returncode=1, stderr="merge conflict between base and head")
        _patch_gh(monkeypatch, lambda _args: update_failure)
        with pytest.raises(SystemExit) as exit_info:
            _update_branch(PR_URL, MAX_FAILED_UPDATES - 1)
        assert exit_info.value.code == 1
        out = capsys.readouterr().out
        assert "::error::could not update the branch" in out
        assert "merge conflict between base and head" in out


class TestRerunFailedChecksOnce:
    def test_reruns_a_failed_check_and_records_its_attempt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _patch_gh(monkeypatch, _rerun_handler(attempt=1, status="completed"))
        before: dict[str, int] = {}
        assert _rerun_failed_checks_once(PR_URL, before) == {"111": 1}
        assert RUN_VIEW_CALL in calls
        assert RERUN_CALL in calls
        assert before == {}

    @pytest.mark.parametrize("status", ["in_progress", "queued"])
    def test_waits_for_the_run_to_complete_before_it_reruns(self, monkeypatch: pytest.MonkeyPatch, status: str) -> None:
        calls = _patch_gh(monkeypatch, _rerun_handler(attempt=1, status=status))
        assert _rerun_failed_checks_once(PR_URL, {}) == {}
        assert RERUN_CALL not in calls

    @pytest.mark.parametrize(("attempt", "status"), [(1, "completed"), (2, "in_progress")])
    def test_waits_for_the_rerun_to_finish(self, monkeypatch: pytest.MonkeyPatch, attempt: int, status: str) -> None:
        calls = _patch_gh(monkeypatch, _rerun_handler(attempt=attempt, status=status))
        assert _rerun_failed_checks_once(PR_URL, {"111": 1}) == {"111": 1}
        assert RERUN_CALL not in calls

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
        reason = "run 111 cannot be rerun; This workflow is already running"
        handler = _rerun_handler(attempt=1, status="completed", rerun_returncode=1, rerun_stderr=reason)
        _patch_gh(monkeypatch, handler)
        with pytest.raises(SystemExit) as exit_info:
            _rerun_failed_checks_once(PR_URL, {})
        assert exit_info.value.code == 1
        out = capsys.readouterr().out
        assert "could not be re-run" in out
        assert reason in out

    def test_exits_when_the_run_cannot_be_read(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def handler(args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("pr", "checks"):
                return _result(_checks_json(("fail", RUN_LINK)), returncode=1)
            return _result(returncode=1, stderr="HTTP 502")

        calls = _patch_gh(monkeypatch, handler)
        with pytest.raises(SystemExit) as exit_info:
            _rerun_failed_checks_once(PR_URL, {})
        assert exit_info.value.code == 1
        assert "HTTP 502" in capsys.readouterr().out
        assert RERUN_CALL not in calls

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
        monkeypatch.setattr(merge_pr_when_green, "POLL_INTERVAL_SECONDS", 30)
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
        calls = _patch_gh(monkeypatch, _loop_handler([already_merged], state="MERGED", behind_by=(2,)))
        main()
        assert calls == [MERGE_CALL, STATE_CALL]

    def test_updates_a_branch_that_fell_behind_main(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)] * 2 + [_result()]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=(1,)))
        main()
        assert calls.count(UPDATE_CALL) == 1
        assert calls[: calls.index(UPDATE_CALL)].count(MERGE_CALL) == 2
        assert calls.count(MERGE_CALL) == 3
        assert "::notice::merged" in capsys.readouterr().out

    def test_updates_a_branch_only_while_it_is_behind(self, monkeypatch: pytest.MonkeyPatch) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)] * 4 + [_result()]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=(1,)))
        main()
        assert calls.count(UPDATE_CALL) == 1
        assert calls.count(MERGE_CALL) == 5

    def test_gives_a_branch_one_poll_to_be_rebuilt_by_its_owner(self, monkeypatch: pytest.MonkeyPatch) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)] * 2 + [_result()]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=(1, 0)))
        main()
        assert UPDATE_CALL not in calls

    def test_exits_when_the_branch_cannot_be_updated(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        update_failure = _result(returncode=1, stderr="merge conflict between base and head")
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=(1,), update=update_failure))
        with pytest.raises(SystemExit) as exit_info:
            main()
        assert exit_info.value.code == 1
        assert calls.count(UPDATE_CALL) == MAX_FAILED_UPDATES
        assert "merge conflict between base and head" in capsys.readouterr().out

    def test_forgets_a_failed_update_once_the_branch_is_current_again(self, monkeypatch: pytest.MonkeyPatch) -> None:
        update_failure = _result(returncode=1, stderr="HTTP 502")
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)] * 6 + [_result()]
        calls = _patch_gh(monkeypatch, _loop_handler(merges, behind_by=(1, 1, 0, 1), update=update_failure))
        main()
        assert calls.count(UPDATE_CALL) == 3

    def test_does_not_rerun_a_failed_check_while_the_branch_is_behind(self, monkeypatch: pytest.MonkeyPatch) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)] * 2 + [_result()]
        calls = _patch_gh(monkeypatch, _with_failed_check(_loop_handler(merges, behind_by=(1,))))
        main()
        assert calls.count(UPDATE_CALL) == 1
        assert RERUN_CALL not in calls

    def test_exits_when_a_check_fails_again_after_one_rerun(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        merges = [_result(returncode=1, stderr=BEHIND_MERGE_ERROR)]
        calls = _patch_gh(monkeypatch, _with_failed_check(_loop_handler(merges)))
        with pytest.raises(SystemExit) as exit_info:
            main()
        assert exit_info.value.code == 1
        assert CHECKS_CALL in calls
        assert calls.count(RERUN_CALL) == 1
        assert "not a flake" in capsys.readouterr().out

    def test_exits_at_the_deadline(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setenv("TIMEOUT_MINUTES", "1")
        calls = _patch_gh(monkeypatch, _loop_handler([_result(returncode=1, stderr=BEHIND_MERGE_ERROR)]))
        with pytest.raises(SystemExit) as exit_info:
            main()
        assert exit_info.value.code == 1
        # The merge attempts come at 0 s, 30 s, and 60 s. The one at 60 s meets the deadline.
        assert calls.count(MERGE_CALL) == 3
        out = capsys.readouterr().out
        assert "could not merge" in out
        assert BEHIND_MERGE_ERROR in out
