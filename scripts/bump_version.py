import subprocess
import sys
from pathlib import Path

import tomlkit


def main() -> None:
    """Get current version, append ".postN" (N=no. of commits since last release), write back into pyproject.toml"""

    # get the latest release tag from git history (e.g. "v9.0.2")
    latest_tag = _make_sys_call("git describe --tags --abbrev=0")

    new_version = _calculate_new_version(latest_tag)

    _write_new_version_into_pyproject_toml(old_version=latest_tag[1:], new_version=new_version)


def _calculate_new_version(latest_tag: str) -> str:
    _check_if_on_main_branch()
    # no. of commits since last release (e.g. "5")
    commit_count_str = _make_sys_call(f"git rev-list --count main ^{latest_tag}")
    # if this CI run was triggered by a release, do nothing
    if commit_count_str == "0":
        sys.exit(0)
    # e.g. 5 -> 4 (N in ".postN" is zero-based)
    commit_count = int(commit_count_str) - 1
    # e.g. "9.0.2.post4" (no leading v in pyproject.toml)
    return f"{latest_tag[1:]}.post{commit_count}"


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
    pyproject_pth = Path("pyproject.toml")
    pyproject = tomlkit.parse(pyproject_pth.read_text(encoding="utf-8"))
    if pyproject["project"]["version"] != old_version:  # type: ignore[index]
        msg = f"Version in pyproject.toml is '{pyproject['project']['version']}', but expected {old_version}"  # type: ignore[index]
        raise ValueError(msg)
    pyproject["project"]["version"] = new_version  # type: ignore[index]
    pyproject_pth.write_text(tomlkit.dumps(pyproject), encoding="utf-8")


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
