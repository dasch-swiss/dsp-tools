import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import tomlkit


@dataclass(frozen=True)
class Package:
    pyproject_path: Path
    tag_prefix: str


DSP_TOOLS = Package(Path("packages/dsp-tools/pyproject.toml"), "v")
DSP_VRE_LIB = Package(Path("packages/dsp-vre-lib/pyproject.toml"), "dsp-vre-lib-v")
PACKAGES = {"dsp-tools": DSP_TOOLS, "dsp-vre-lib": DSP_VRE_LIB}


def main() -> None:
    """Write the version "<last release>.postN" (N = no. of commits since that release) into the package's pyproject."""
    match sys.argv[1:]:
        case [name] if name in PACKAGES:
            package = PACKAGES[name]
        case _:
            sys.exit(f"usage: bump_version.py {{{' | '.join(PACKAGES)}}}")
    released_version, new_version = _calculate_new_version(package)
    _write_new_version_into_pyproject_toml(package.pyproject_path, released_version, new_version)


def _calculate_new_version(package: Package) -> tuple[str, str]:
    """Return the released version and the post-release version. Exit if this commit is the release itself."""
    _check_if_on_main_branch()
    latest_tag = _latest_release_tag(package.tag_prefix)
    if latest_tag:
        released_version = latest_tag.removeprefix(package.tag_prefix)
        commit_count_str = _make_sys_call(f"git rev-list --count main ^{latest_tag}")
    else:
        # A package without a release yet counts all commits, from the version in its pyproject.
        released_version = _read_version(package.pyproject_path)
        commit_count_str = _make_sys_call("git rev-list --count main")
    # if this CI run was triggered by a release, do nothing
    if commit_count_str == "0":
        sys.exit(0)
    return released_version, _post_release_version(released_version, int(commit_count_str))


def _latest_release_tag(tag_prefix: str) -> str | None:
    """The highest release tag of the package on main, for example "v9.0.2" or "dsp-vre-lib-v0.1.0"."""
    tags = _make_sys_call(f"git tag --merged main --list {tag_prefix}[0-9]* --sort=-v:refname")
    return tags.splitlines()[0] if tags else None


def _post_release_version(released_version: str, commit_count: int) -> str:
    """
    Build the post-release version, for example "9.0.2" with 5 commits gives "9.0.2.post4".

    The N in ".postN" is zero-based.
    """
    return f"{released_version}.post{commit_count - 1}"


def _check_if_on_main_branch() -> None:
    if _make_sys_call("git rev-parse --abbrev-ref HEAD") != "main":
        msg = (
            "The 'git rev-list' command will only work as expected on the main branch. "
            "If this workflow is intentionally run on a branch other than 'main', "
            "run 'git rev-list' with 'HEAD' instead of 'main'. "
            "This should only be done for testing purposes. In production, this will yield an unintended commit count."
        )
        raise ValueError(msg)


def _read_version(pyproject_path: Path) -> str:
    return str(tomlkit.parse(pyproject_path.read_text(encoding="utf-8"))["project"]["version"])


def _write_new_version_into_pyproject_toml(pyproject_path: Path, old_version: str, new_version: str) -> None:
    pyproject = tomlkit.parse(pyproject_path.read_text(encoding="utf-8"))
    if pyproject["project"]["version"] != old_version:
        msg = f"Version in pyproject.toml is '{pyproject['project']['version']}', but expected {old_version}"
        raise ValueError(msg)
    pyproject["project"]["version"] = new_version
    pyproject_path.write_text(tomlkit.dumps(pyproject), encoding="utf-8")


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
