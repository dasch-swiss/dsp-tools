"""
Script to automate bumping the Docker image versions of DSP components.
This script is meant to be run in the GitHub Actions CI. See `.github/workflows/bump-stack-versions.yml`.

Reads the release version and component versions from environment variables,
writes src/dsp_tools/resources/start-stack/versions.env, creates a branch,
commits, pushes, and opens a pull request. The docker-compose.yml interpolates
the version values at `docker compose up` time via `--env-file versions.env`.

The URL of the created PR is written to $GITHUB_OUTPUT as `pr_url`, so the
workflow can merge exactly that PR instead of searching for it afterwards.
No output means no PR was opened (versions.env was already up to date).

Prerequisites:
- RELEASE, API, APP, DB env vars must be set
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VERSIONS_ENV_PATH = Path("src/dsp_tools/resources/start-stack/versions.env")

_RELEASE_RE: re.Pattern[str] = re.compile(r"\d{4}\.\d{2}\.\d{2}")


def main() -> None:
    print("Bumping versions ...")

    release, versions = _get_versions_from_env()
    _write_versions_env(release, versions)

    if not _has_diff():
        print("versions.env is already up to date. Nothing to do.")
        sys.exit(0)

    git_msg = f"chore(start-stack): bump versions to {release}"
    branch_name = f"chore/bump-version-{release}"
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", str(VERSIONS_ENV_PATH)], check=True)
    subprocess.run(["git", "commit", "-m", git_msg], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

    # stdout is captured to get the PR URL; stderr stays inherited so gh's
    # diagnostics still show up in the CI log if the call fails.
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            git_msg,
            "--base",
            "main",
            "--body",
            "",
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    pr_url = _parse_pr_url(result.stdout)
    print(f"Pull request created for branch '{branch_name}': {pr_url}")
    _write_github_output("pr_url", pr_url)


def _parse_pr_url(gh_stdout: str) -> str:
    # `gh pr create` prints the URL of the new PR as the last line of stdout.
    lines = [line.strip() for line in gh_stdout.splitlines() if line.strip()]
    if not lines or not lines[-1].startswith("https://"):
        print(f"ERROR: could not parse the PR URL from the output of `gh pr create`: {gh_stdout!r}")
        sys.exit(1)
    return lines[-1]


def _write_github_output(name: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:  # running outside GitHub Actions
        return
    with Path(github_output).open("a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")


def _get_versions_from_env() -> tuple[str, dict[str, str]]:
    release = _require_env("RELEASE")
    if not _RELEASE_RE.fullmatch(release):
        print(f"ERROR: RELEASE must match YYYY.MM.DD, got: {release!r}")
        sys.exit(1)
    return release, {
        "api": _require_env("API"),
        "app": _require_env("APP"),
        "db": _require_env("DB"),
    }


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} env var is not set.")
        sys.exit(1)
    return value


def _write_versions_env(release: str, versions: dict[str, str]) -> None:
    # POSIX-shell-sourceable. Consumed by:
    #   - src/dsp_tools/resources/start-stack/docker-compose.yml at
    #     `docker compose --env-file versions.env up` time
    #     (image: daschswiss/knora-api:${API} etc.)
    #   - src/dsp_tools/commands/start_stack/start_stack.py at runtime (reads API
    #     to construct the dsp-api raw-content URL prefix)
    #   - test/e2e/setup_testcontainers/setup.py for testcontainer image tags
    #   - .github/workflows/publish-release-to-pypi.yml (dispatcher) via
    #     `grep '^[A-Z]+=' >> $GITHUB_ENV` — keys flow into the dsp-docs bump
    #
    # Any change to the KEY=VALUE shape (quoting, multi-line values, extra
    # whitespace) breaks the dispatcher's grep-into-$GITHUB_ENV pattern.
    content = (
        "# Auto-managed by .github/workflows/bump-stack-versions.yml. Do not edit by hand.\n"
        f"RELEASE={release}\n"
        f"API={versions['api']}\n"
        f"APP={versions['app']}\n"
        f"DB={versions['db']}\n"
    )
    # newline="\n" guarantees LF output on every platform so the file is
    # byte-identical across CI and local runs.
    VERSIONS_ENV_PATH.write_text(content, encoding="utf-8", newline="\n")


def _has_diff() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", str(VERSIONS_ENV_PATH)],
        check=False,
    )
    return result.returncode != 0


if __name__ == "__main__":
    main()
