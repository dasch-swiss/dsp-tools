"""Script to automate bumping the Docker image versions of DSP components.

Reads the release version and component versions from the VERSION_JSON environment variable,
updates src/dsp_tools/resources/start-stack/docker-compose.yml,
creates a branch, commits, pushes, and opens a pull request.

Prerequisites:
- git must be installed and the working tree must be on a clean main branch
- gh CLI must be installed and authenticated (gh auth login)
- VERSION_JSON env var must be set (e.g. {"release":"2026.10.02","api":"v35.3.0","app":"v12.10.0","db":"5.5.0-3"})
"""

from __future__ import annotations

import json
import os
import re
import shutil
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
    _check_gh_installed()
    _check_gh_authenticated()

    print("Bumping versions ...")

    subprocess.run(["git", "pull"], check=True)

    version_key, versions = _get_versions_from_env()

    old_content = DOCKER_COMPOSE_PATH.read_text(encoding="utf-8")
    new_content = _update_compose_content(old_content, versions)
    DOCKER_COMPOSE_PATH.write_text(new_content, encoding="utf-8")

    if not _has_diff():
        print("docker-compose.yml is already up to date. Nothing to do.")
        sys.exit(0)

    git_msg = f"chore(start-stack): bump version to {version_key}"

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
            f"chore(start-stack): {git_msg}",
            "--base",
            "main",
            "--body",
            "",
        ],
        check=True,
    )
    print(f"Pull request created for branch '{branch_name}'.")


def _check_gh_installed() -> None:
    if shutil.which("gh") is None:
        print("ERROR: 'gh' CLI is not installed. Install it from https://cli.github.com/")
        sys.exit(1)


def _check_gh_authenticated() -> None:
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, check=False)
    if result.returncode != 0:
        print("ERROR: Not authenticated with GitHub. Run 'gh auth login' first.")
        sys.exit(1)


def _get_versions_from_env() -> tuple[str, dict[str, str]]:
    version_json = os.environ.get("VERSION_JSON")
    if not version_json:
        print("ERROR: VERSION_JSON is not set. Provide a JSON string with release + component versions.")
        sys.exit(1)
    try:
        data: dict[str, str] = json.loads(version_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: VERSION_JSON is not valid JSON: {e}")
        sys.exit(1)
    release = data.pop("release", None)
    if not release:
        print("ERROR: VERSION_JSON must contain a 'release' key.")
        sys.exit(1)
    return release, data


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
