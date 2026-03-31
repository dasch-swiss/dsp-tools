"""
Script to automate bumping the Docker image versions of DSP components.
This script is meant to be run in the GitHub Actions CI. See `.github/workflows/bump-stack-versions.yml`.

Reads the release version and component versions from environment variables,
updates src/dsp_tools/resources/start-stack/docker-compose.yml,
creates a branch, commits, pushes, and opens a pull request.

Prerequisites:
- RELEASE, API, APP, DB env vars must be set
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DOCKER_COMPOSE_PATH = Path("src/dsp_tools/resources/start-stack/docker-compose.yml")

# Each entry maps a regex pattern (capturing the image prefix up to and including the colon)
# to the corresponding key in RELEASE.json.
IMAGE_SUBSTITUTIONS: list[tuple[str, str]] = [
    (r"(daschswiss/knora-api:)[^\s]+", "api"),
    (r"(daschswiss/knora-sipi:)[^\s]+", "api"),
    (r"(daschswiss/dsp-ingest:)[^\s]+", "api"),
    (r"(daschswiss/dsp-app:)[^\s]+", "app"),
    (r"(daschswiss/apache-jena-fuseki:)[^\s]+", "db"),
]


def main() -> None:
    print("Bumping versions ...")

    version_key, versions = _get_versions_from_env()

    old_content = DOCKER_COMPOSE_PATH.read_text(encoding="utf-8")
    new_content = _update_compose_content(old_content, versions)
    DOCKER_COMPOSE_PATH.write_text(new_content, encoding="utf-8")

    if not _has_diff():
        print("docker-compose.yml is already up to date. Nothing to do.")
        sys.exit(0)

    git_msg = f"chore(start-stack): bump versions to {version_key}"

    branch_name = f"chore/bump-version-{version_key}"
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", str(DOCKER_COMPOSE_PATH)], check=True)
    subprocess.run(["git", "commit", "-m", git_msg], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

    subprocess.run(
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
    )
    print(f"Pull request created for branch '{branch_name}'.")


def _get_versions_from_env() -> tuple[str, dict[str, str]]:
    release = _require_env("RELEASE")
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


def _update_compose_content(content: str, versions: dict[str, str]) -> str:
    for pattern, version_key in IMAGE_SUBSTITUTIONS:
        content = re.sub(pattern, r"\g<1>" + versions[version_key], content)
    return content


def _has_diff() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", str(DOCKER_COMPOSE_PATH)],
        check=False,
    )
    return result.returncode != 0


if __name__ == "__main__":
    main()
