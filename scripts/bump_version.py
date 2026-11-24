import subprocess
import sys
from pathlib import Path

import tomlkit

PYPROJECT_PATH = Path("packages/dsp-tools/pyproject.toml")


def main() -> None:
    """Get current version, append ".postN" (N=no. of commits since last release), write back into pyproject.toml"""

    # get the latest dsp-tools release tag from git history (e.g. "v9.0.2"),
    # ignoring the tags of other packages in the workspace (e.g. "dsp-vre-v0.1.0")
    latest_tag = _make_sys_call("git describe --tags --abbrev=0 --match v[0-9]*")

    new_version = _calculate_new_version(latest_tag)

    _write_new_version_into_pyproject_toml(old_version=latest_tag[1:], new_version=new_version)


def _calculate_new_version(latest_tag: str) -> str:
    _check_if_on_main_branch()
    # no. of commits since last release (e.g. "5")
    commit_count_str = _make_sys_call(f"git rev-list --count main ^{latest_tag}")
    # if this CI run was triggered by a release, do nothing
    if commit_count_str == "0":
        sys.exit(0)
    return _post_release_version(latest_tag, int(commit_count_str))


def _post_release_version(latest_tag: str, commit_count: int) -> str:
    """
    Build the post-release version, for example "v9.0.2" with 5 commits gives "9.0.2.post4".

    The N in ".postN" is zero-based, and pyproject.toml has no leading "v".
    """
    return f"{latest_tag[1:]}.post{commit_count - 1}"


def _check_if_on_main_branch() -> None:
    if _make_sys_call("git rev-parse --abbrev-ref HEAD") != "main":
        msg = (
            "The 'git rev-list' command will only work as expected on the main branch. "
            "If this workflow is intentionally run on a branch other than 'main', "
            "run 'git rev-list' with 'HEAD' instead of 'main'. "
            "This should only be done for testing purposes. In production, this will yield an unintended commit count."
        )
        raise ValueError(msg)


def _write_new_version_into_pyproject_toml(old_version: str, new_version: str) -> None:
    pyproject = tomlkit.parse(PYPROJECT_PATH.read_text(encoding="utf-8"))
    if pyproject["project"]["version"] != old_version:
        msg = f"Version in pyproject.toml is '{pyproject['project']['version']}', but expected {old_version}"
        raise ValueError(msg)
    pyproject["project"]["version"] = new_version
    PYPROJECT_PATH.write_text(tomlkit.dumps(pyproject), encoding="utf-8")


def _make_sys_call(call: str) -> str:
    try:
        res = subprocess.run(call.split(), capture_output=True, check=True, encoding="utf-8").stdout.removesuffix("\n")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Call: {call} | Returncode: {e.returncode} | Stdout: {e.stdout} | Stderr: {e.stderr}")
        sys.exit(1)
    print(f"INFO: Call: {call} | Stdout: {res}")
    return res


if __name__ == "__main__":
    main()
