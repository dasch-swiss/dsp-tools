"""
Merges a pull request as soon as its required status checks pass. Meant to run in CI, not locally.

Retries `gh pr merge --squash --admin` until it succeeds or the time budget ends.
Between two attempts, it re-runs a failed required check once.
It also updates the PR branch when the branch stays behind its base branch.
The composite action .github/actions/merge-pr-when-green calls this script.

Prerequisites:
- PR_URL, TIMEOUT_MINUTES, GITHUB_REPOSITORY env vars must be set
- GH_TOKEN env var must hold the token of a review-bypass actor,
  with contents, pull-requests, and actions write access
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

POLL_INTERVAL_SECONDS = 30
# As of October 2026, release-please can rebuild its release branch on each push to main
# (.github/workflows/release-please.yml). So a branch that is behind gets one poll to be rebuilt first.
BEHIND_POLLS_BEFORE_UPDATE = 2
# A branch update that fails this often in a row, for example on a merge conflict, ends the step.
MAX_FAILED_UPDATES = 3

_RUN_ID_RE: re.Pattern[str] = re.compile(r"/actions/runs/(\d+)")


def main() -> None:
    pr_url = _require_env("PR_URL")
    timeout_minutes = int(_require_env("TIMEOUT_MINUTES"))
    repo = _require_env("GITHUB_REPOSITORY")
    print(f"::notice::merging {pr_url} once required checks pass (App bypasses the review)")
    deadline = time.monotonic() + timeout_minutes * 60
    reran_at_attempt: dict[str, int] = {}
    behind_polls = 0
    failed_updates = 0
    while not _try_merge(pr_url):
        if _is_merged(pr_url):
            break
        if time.monotonic() >= deadline:
            print(f"::error::could not merge {pr_url} within budget (check failing or branch blocked)")
            sys.exit(1)
        # As of October 2026, main requires an up-to-date branch.
        # So a branch that is behind gets an update, not a re-run of its checks.
        behind_polls = behind_polls + 1 if _is_behind_base(pr_url, repo) else 0
        if behind_polls == 0:
            failed_updates = 0
            reran_at_attempt = _rerun_failed_checks_once(pr_url, reran_at_attempt)
        elif behind_polls >= BEHIND_POLLS_BEFORE_UPDATE:
            failed_updates = _update_branch(pr_url, failed_updates)
        else:
            print(f"::notice::{pr_url} is behind its base branch; it gets one poll before the update")
        time.sleep(POLL_INTERVAL_SECONDS)
    print(f"::notice::merged {pr_url}")


def _try_merge(pr_url: str) -> bool:
    # As of October 2026, the App bypasses the review only.
    # Required status checks have no per-actor bypass, so the server rejects the merge until every check passes.
    result = _gh("pr", "merge", "--squash", "--admin", pr_url, check=False)
    if result.returncode != 0:
        print(f"{result.stdout}{result.stderr}".strip())
    return result.returncode == 0


def _is_merged(pr_url: str) -> bool:
    result = _gh("pr", "view", pr_url, "--json", "state", "--jq", ".state", check=False)
    return result.stdout.strip() == "MERGED"


def _rerun_failed_checks_once(pr_url: str, reran_at_attempt: dict[str, int]) -> dict[str, int]:
    # As of October 2026, a failed required check does not turn green on its own,
    # and GitHub refuses to re-run a run while any of its jobs still runs.
    # So wait until the run is complete, re-run it once, and give up as soon as the re-run has failed too.
    updated = dict(reran_at_attempt)
    for run_id in _failed_required_run_ids(pr_url):
        view = _gh("run", "view", run_id, "--json", "attempt,status", check=False)
        if view.returncode != 0:
            print(f"::error::could not read run {run_id}: {view.stderr.strip()}")
            sys.exit(1)
        run = json.loads(view.stdout)
        if run["status"] != "completed":
            continue
        attempt = int(run["attempt"])
        if run_id not in updated:
            print(f"::notice::required check in run {run_id} failed; re-running it once in case it is a flake")
            rerun = _gh("run", "rerun", run_id, "--failed", check=False)
            if rerun.returncode != 0:
                reason = rerun.stderr.strip()
                print(f"::error::required check in run {run_id} failed and could not be re-run: {reason}")
                sys.exit(1)
            # Compare with the attempt seen before the re-run.
            # Otherwise the failure that caused the re-run reads as a second failure.
            updated[run_id] = attempt
        elif attempt > updated[run_id]:
            print(f"::error::required check in run {run_id} failed again after a re-run — not a flake")
            sys.exit(1)
    return updated


def _failed_required_run_ids(pr_url: str) -> list[str]:
    # As of October 2026, `gh pr checks` exits non-zero while checks fail or wait.
    # It prints no JSON while no check is reported.
    result = _gh("pr", "checks", pr_url, "--required", "--json", "bucket,link", check=False)
    try:
        checks = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"could not read the checks of {pr_url}: {result.stderr.strip()}")
        return []
    links = [check["link"] for check in checks if check["bucket"] in ("fail", "cancel")]
    matches = [_RUN_ID_RE.search(link) for link in links]
    return sorted({match.group(1) for match in matches if match})


def _is_behind_base(pr_url: str, repo: str) -> bool:
    # As of October 2026, the merge error of a branch that is behind its base lists the required checks as "expected".
    # It never says "behind", so ask the compare API.
    # A lookup that fails counts as not behind, so that the loop goes on polling.
    try:
        return _commits_behind_base(pr_url, repo) > 0
    except subprocess.CalledProcessError as error:
        reason = error.stderr.strip()
    except (ValueError, KeyError, TypeError) as error:
        reason = f"unexpected answer ({error!r})"
    print(f"::warning::could not tell whether {pr_url} is behind its base: {reason}")
    return False


def _commits_behind_base(pr_url: str, repo: str) -> int:
    pr = json.loads(_gh("pr", "view", pr_url, "--json", "baseRefName,headRefOid").stdout)
    basehead = f"{pr['baseRefName']}...{pr['headRefOid']}"
    comparison = json.loads(_gh("api", f"repos/{repo}/compare/{basehead}").stdout)
    return int(comparison["behind_by"])


def _update_branch(pr_url: str, failed_updates: int) -> int:
    # Call it only for a branch that is behind: an update at every poll would restart the checks every time.
    # Returns the number of failed updates in a row.
    print(f"::notice::updating the branch of {pr_url}, which is behind its base branch")
    result = _gh("pr", "update-branch", pr_url, check=False)
    if result.returncode == 0:
        return 0
    message = f"could not update the branch of {pr_url}: {result.stderr.strip()}"
    if failed_updates + 1 >= MAX_FAILED_UPDATES:
        print(f"::error::{message}")
        sys.exit(1)
    print(f"::warning::{message}")
    return failed_updates + 1


def _gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} env var is not set.")
        sys.exit(1)
    return value


if __name__ == "__main__":
    main()
