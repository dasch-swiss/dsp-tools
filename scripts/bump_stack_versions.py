"""Script to automate bumping the Docker image versions of DSP components.

Fetches the latest version from dasch-swiss/ops-deploy/versions/RELEASE.json,
updates src/dsp_tools/resources/start-stack/docker-compose.yml,
creates a branch, commits, pushes, and opens a pull request.

Prerequisites:
- git must be installed and the working tree must be on a clean main branch
- gh CLI must be installed and authenticated (gh auth login)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

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
    _check_on_main_branch()
    _check_working_tree_clean()

    print("Bumping versions ...")

    subprocess.run(["git", "pull"], check=True)

    release_data = _fetch_release_json()
    version_key, versions = _get_latest_release(release_data)

    old_content = DOCKER_COMPOSE_PATH.read_text(encoding="utf-8")
    new_content = _update_compose_content(old_content, versions)
    DOCKER_COMPOSE_PATH.write_text(new_content, encoding="utf-8")

    if not _has_diff():
        print(f"{BACKGROUND_BOLD_RED}docker-compose.yml is already up to date. Nothing to do.{RESET_TO_DEFAULT}")
        sys.exit(1)

    git_msg = f"bump versions to {version_key}"

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


def _check_on_main_branch() -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    branch = result.stdout.strip()
    if branch != "main":
        print(f"ERROR: Must be on the 'main' branch, but currently on '{branch}'.")
        sys.exit(1)


def _check_working_tree_clean() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    if result.stdout.strip():
        print("ERROR: Working tree is not clean. Please commit or stash your changes first.")
        print(result.stdout)
        sys.exit(1)


def _fetch_release_json() -> dict[str, dict[str, str]]:
    result = subprocess.run(
        [
            "gh",
            "api",
            "repos/dasch-swiss/ops-deploy/contents/versions/RELEASE.json",
            "--header",
            "Accept: application/vnd.github.raw+json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)  # type: ignore[no-any-return]


def _get_latest_release(data: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    latest_key = max(data.keys())
    return latest_key, data[latest_key]


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
