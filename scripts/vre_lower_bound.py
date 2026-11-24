"""
The only writer of the dsp-vre dependency of dsp-tools (packages/dsp-tools/pyproject.toml).

Subcommands:
- `raise <version>`: raises the lower bound to <version>.
  The release workflow runs it on the dsp-tools release PR, with the latest released dsp-vre version.
- `check-on-pypi`: fails if the lower bound is not on PyPI. CI runs it on the dsp-tools release PR.
- `pin <version>`: requires exactly <version>. The dev-release workflow runs it, with the dsp-vre dev version
  that it publishes from the same commit.

`raise` and `check-on-pypi` do nothing if dsp-tools does not declare dsp-vre.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import tomlkit
from packaging.requirements import Requirement
from packaging.specifiers import Specifier
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import Version

PYPROJECT_PATH = Path("packages/dsp-tools/pyproject.toml")
PACKAGE_NAME = "dsp-vre"
PYPI_URL = "https://pypi.org/pypi/dsp-vre/{version}/json"
# The form `>=X,<Y` (see the set-up document). Other operators make the lower bound unclear.
ALLOWED_OPERATORS = {">=", "<", "<=", "!="}


def main() -> None:
    match sys.argv[1:]:
        case ["raise", version]:
            raise_lower_bound_in_pyproject(PYPROJECT_PATH, version)
        case ["check-on-pypi"]:
            check_lower_bound_on_pypi(PYPROJECT_PATH)
        case ["pin", version]:
            pin_in_pyproject(PYPROJECT_PATH, version)
        case _:
            sys.exit("usage: vre_lower_bound.py raise <version> | check-on-pypi | pin <version>")


def raise_lower_bound(dependency: str, version: str) -> str:
    """Return the dependency string with the lower bound `>=version`, if `version` is higher than the current bound."""
    version = str(Version(version))
    requirement = Requirement(dependency)
    current = _lower_bound(requirement)
    if current is not None and current >= Version(version):
        return dependency
    other_specifiers = [s for s in requirement.specifier if s.operator != ">="]
    requirement.specifier = SpecifierSet([*other_specifiers, Specifier(f">={version}")])
    if not requirement.specifier.contains(version, prereleases=True):
        msg = f"{version} does not satisfy the dependency '{dependency}'. Change the upper bound by hand."
        raise ValueError(msg)
    return str(requirement)


def raise_lower_bound_in_pyproject(pyproject: Path, version: str) -> None:
    """Change only the dsp-vre line, as plain text, so that the formatting and the comments stay."""
    text = pyproject.read_text(encoding="utf-8")
    dependency = _find_dependency(text)
    if dependency is None:
        print(f"dsp-tools does not declare {PACKAGE_NAME}: no change")
        return
    raised = raise_lower_bound(dependency, version)
    if f'"{dependency}"' not in text:
        sys.exit(f"The text '\"{dependency}\"' is not in {pyproject}. Change the dependency by hand.")
    pyproject.write_text(text.replace(f'"{dependency}"', f'"{raised}"', 1), encoding="utf-8")
    print(f"{PACKAGE_NAME} dependency: '{dependency}' -> '{raised}'")


def pin_in_pyproject(pyproject: Path, version: str) -> None:
    """Replace the dsp-vre line, as plain text, by an exact pin, so that the formatting and the comments stay."""
    text = pyproject.read_text(encoding="utf-8")
    dependency = _find_dependency(text)
    if dependency is None:
        sys.exit(f"dsp-tools does not declare {PACKAGE_NAME}: nothing to pin")
    if f'"{dependency}"' not in text:
        sys.exit(f"The text '\"{dependency}\"' is not in {pyproject}. Change the dependency by hand.")
    pinned = f"{PACKAGE_NAME}=={Version(version)}"
    pyproject.write_text(text.replace(f'"{dependency}"', f'"{pinned}"', 1), encoding="utf-8")
    print(f"{PACKAGE_NAME} dependency: '{dependency}' -> '{pinned}'")


def check_lower_bound_on_pypi(pyproject: Path) -> None:
    dependency = _find_dependency(pyproject.read_text(encoding="utf-8"))
    if dependency is None:
        print(f"dsp-tools does not declare {PACKAGE_NAME}: nothing to check")
        return
    lower_bound = _lower_bound(Requirement(dependency))
    if lower_bound is None:
        sys.exit(f"The dependency '{dependency}' has no lower bound (>=).")
    if not is_on_pypi(str(lower_bound)):
        sys.exit(f"{PACKAGE_NAME} {lower_bound} is not on PyPI. Release {PACKAGE_NAME} first.")
    print(f"{PACKAGE_NAME} {lower_bound} is on PyPI")


def is_on_pypi(version: str) -> bool:
    """A yanked version counts as not on PyPI. Other errors than 404 propagate, so that CI fails loudly."""
    try:
        # PYPI_URL is a fixed https URL, thus no file: or custom scheme.
        with urllib.request.urlopen(PYPI_URL.format(version=version), timeout=30) as response:  # noqa: S310
            return not json.load(response)["info"]["yanked"]
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise


def _find_dependency(pyproject_text: str) -> str | None:
    dependencies: list[str] = tomlkit.parse(pyproject_text)["project"].get("dependencies", [])
    matches = [str(d) for d in dependencies if canonicalize_name(Requirement(str(d)).name) == PACKAGE_NAME]
    if len(matches) > 1:
        sys.exit(f"dsp-tools declares {PACKAGE_NAME} more than one time: {matches}. Change the dependency by hand.")
    return matches[0] if matches else None


def _lower_bound(requirement: Requirement) -> Version | None:
    other_operators = {s.operator for s in requirement.specifier} - ALLOWED_OPERATORS
    if other_operators:
        msg = f"The dependency '{requirement}' uses {sorted(other_operators)}. Use the form '{PACKAGE_NAME}>=X,<Y'."
        raise ValueError(msg)
    bounds = [Version(s.version) for s in requirement.specifier if s.operator == ">="]
    return max(bounds) if bounds else None


if __name__ == "__main__":
    main()
