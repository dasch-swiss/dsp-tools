import subprocess  # noqa: INP001 (missing __init__.py)
import sys
from pathlib import Path

import tomlkit


def _make_sys_call(call: str) -> str:
    try:
        return subprocess.run(call.split(), capture_output=True, check=True, encoding="utf-8").stdout.removesuffix("\n")
    except subprocess.CalledProcessError as e:
        print(f"Returncode: {e.returncode} | Stdout: {e.stdout} | Stderr: {e.stderr}")
        raise e from None


def main() -> None:
    """Get current version, append ".postN" (N=no. of commits since last release), write back into pyproject.toml"""
    # get the latest release tag from git history (e.g. "v9.0.2")
    latest_tag = _make_sys_call("git describe --tags --abbrev=0")
    # get the number of commits since the last release (e.g. "5")
    commit_count_str = _make_sys_call(f"git rev-list --count main ^{latest_tag}")
    # if this CI run was triggered by a release, do nothing
    if commit_count_str == "0":
        sys.exit(0)
    # e.g. 5 -> 4 (N in ".postN" is zero-based)
    commit_count = int(commit_count_str) - 1
    # e.g. "9.0.2.post4" (no leading v in pyproject.toml)
    new_version = f"{latest_tag[1:]}.post{commit_count}"
    # write new version into pyproject.toml
    pyproject_pth = Path("pyproject.toml")
    pyproject = tomlkit.parse(pyproject_pth.read_text(encoding="utf-8"))
    if pyproject["project"]["version"] != latest_tag[1:]:  # type: ignore[index]
        msg = f"Version in pyproject.toml is '{pyproject["project"]["version"]}', but expected {latest_tag[1:]}"  # type: ignore[index]
        raise ValueError(msg)
    pyproject["project"]["version"] = new_version  # type: ignore[index]
    pyproject_pth.write_text(tomlkit.dumps(pyproject), encoding="utf-8")


if __name__ == "__main__":
    main()
