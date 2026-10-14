"""
Merges a pull request as soon as its required status checks pass. Meant to run in CI, not locally.

Retries `gh pr merge --squash --admin` until it succeeds or the time budget ends.
Between two attempts, it re-runs a failed required check once.
It also updates the PR branch when the branch falls behind its base branch.
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

_RUN_ID_RE: re.Pattern[str] = re.compile(r"/actions/runs/(\d+)")


def main() -> None:
    pr_url = _require_env("PR_URL")
    timeout_minutes = int(_require_env("TIMEOUT_MINUTES"))
    repo = _require_env("GITHUB_REPOSITORY")
    print(f"::notice::merging {pr_url} once required checks pass (App bypasses the review)")
    deadline = time.monotonic() + timeout_minutes * 60
    reran_at_attempt: dict[str, int] = {}
    while not _try_merge(pr_url):
        if _is_merged(pr_url):
            break
        if time.monotonic() >= deadline:
            print(f"::error::could not merge {pr_url} within budget (check failing or branch blocked)")
            sys.exit(1)
        reran_at_attempt = _rerun_failed_checks_once(pr_url, reran_at_attempt)
        _update_branch_if_behind(pr_url, repo)
        time.sleep(POLL_INTERVAL_SECONDS)
    print(f"::notice::merged {pr_url}")


def _try_merge(pr_url: str) -> bool:
    # The App bypasses the review only: required status checks have no per-actor bypass.
    # So the server rejects the merge until every check passes, and its message always names the missing review.
    result = _gh("pr", "merge", "--squash", "--admin", pr_url, check=False)
    if result.returncode != 0:
        print(f"{result.stdout}{result.stderr}".strip())
    return result.returncode == 0


def _is_merged(pr_url: str) -> bool:
    result = _gh("pr", "view", pr_url, "--json", "state", "--jq", ".state", check=False)
    return result.stdout.strip() == "MERGED"


def _rerun_failed_checks_once(pr_url: str, reran_at_attempt: dict[str, int]) -> dict[str, int]:
    # A required check in a terminal `fail` state never turns green on its own.
    # Re-run it once, then give up as soon as the re-run has failed too.
    updated = dict(reran_at_attempt)
    for run_id in _failed_required_run_ids(pr_url):
        run = json.loads(_gh("run", "view", run_id, "--json", "attempt,status").stdout)
        attempt = int(run["attempt"])
        if run_id not in updated:
            print(f"::notice::required check in run {run_id} failed; re-running it once in case it is a flake")
            if _gh("run", "rerun", run_id, "--failed", check=False).returncode != 0:
                print(f"::error::required check in run {run_id} failed and could not be re-run")
                sys.exit(1)
            # Compare with the attempt seen before the re-run.
            # Otherwise the failure that caused the re-run reads as a second failure.
            updated[run_id] = attempt
        elif run["status"] == "completed" and attempt > updated[run_id]:
            print(f"::error::required check in run {run_id} failed again after a re-run — not a flake")
            sys.exit(1)
    return updated


def _failed_required_run_ids(pr_url: str) -> list[str]:
    # `gh pr checks` exits non-zero while checks fail or wait. It prints no JSON while no check is reported.
    result = _gh("pr", "checks", pr_url, "--required", "--json", "bucket,link", check=False)
    try:
        checks = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    links = [check["link"] for check in checks if check["bucket"] == "fail"]
    matches = [_RUN_ID_RE.search(link) for link in links]
    return sorted({match.group(1) for match in matches if match})


def _update_branch_if_behind(pr_url: str, repo: str) -> None:
    # A branch behind base can never merge, but the merge error then lists its checks as "expected".
    # It never says "behind", so ask the compare API.
    try:
        behind_by = _commits_behind_base(pr_url, repo)
    except subprocess.CalledProcessError as error:
        print(f"::warning::could not tell whether {pr_url} is behind its base: {error.stderr.strip()}")
        return
    # Update only when behind. An update at every poll would restart the checks every time.
    if behind_by == 0:
        return
    print(f"::notice::branch behind base by {behind_by} commits; updating")
    result = _gh("pr", "update-branch", pr_url, check=False)
    if result.returncode != 0:
        print(f"::warning::could not update the branch of {pr_url}: {result.stderr.strip()}")


def _commits_behind_base(pr_url: str, repo: str) -> int:
    pr = json.loads(_gh("pr", "view", pr_url, "--json", "baseRefName,headRefOid").stdout)
    basehead = f"{pr['baseRefName']}...{pr['headRefOid']}"
    comparison = json.loads(_gh("api", f"repos/{repo}/compare/{basehead}").stdout)
    return int(comparison["behind_by"])


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
