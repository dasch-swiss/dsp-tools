from pathlib import Path

import pytest

from scripts import vre_lib_lower_bound
from scripts.vre_lib_lower_bound import check_lower_bound_on_pypi
from scripts.vre_lib_lower_bound import raise_lower_bound
from scripts.vre_lib_lower_bound import raise_lower_bound_in_pyproject

PYPROJECT_TEMPLATE = """\
[project]
name = "dsp-tools"
version = "19.3.4"
dependencies = [
    "jinja2",
    {vre_lib}
    "yaspin",
]
"""


def _write_pyproject(tmp_path: Path, vre_lib_line: str) -> Path:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(PYPROJECT_TEMPLATE.format(vre_lib=vre_lib_line), encoding="utf-8")
    return pyproject


class TestRaiseLowerBound:
    def test_raises_lower_bound_and_keeps_upper_bound(self) -> None:
        assert raise_lower_bound("dsp-vre-lib>=0.1,<0.2", "0.1.3") == "dsp-vre-lib<0.2,>=0.1.3"

    def test_adds_lower_bound_if_missing(self) -> None:
        assert raise_lower_bound("dsp-vre-lib<0.2", "0.1.3") == "dsp-vre-lib<0.2,>=0.1.3"

    def test_keeps_a_higher_lower_bound(self) -> None:
        assert raise_lower_bound("dsp-vre-lib>=0.1.5,<0.2", "0.1.3") == "dsp-vre-lib>=0.1.5,<0.2"

    def test_keeps_an_equal_lower_bound(self) -> None:
        assert raise_lower_bound("dsp-vre-lib>=0.1.3,<0.2", "0.1.3") == "dsp-vre-lib>=0.1.3,<0.2"

    def test_fails_if_the_version_is_outside_the_upper_bound(self) -> None:
        with pytest.raises(ValueError, match=r"0\.2\.0 does not satisfy"):
            raise_lower_bound("dsp-vre-lib>=0.1,<0.2", "0.2.0")


class TestRaiseLowerBoundInPyproject:
    def test_changes_only_the_vre_lib_line(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2",  # keep this comment')
        raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        expected = PYPROJECT_TEMPLATE.format(vre_lib='"dsp-vre-lib<0.2,>=0.1.3",  # keep this comment')
        assert pyproject.read_text(encoding="utf-8") == expected

    def test_no_change_without_vre_lib_dependency(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"lxml",')
        before = pyproject.read_text(encoding="utf-8")
        raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        assert pyproject.read_text(encoding="utf-8") == before


class TestCheckLowerBoundOnPypi:
    def test_passes_if_the_lower_bound_is_on_pypi(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1.3,<0.2",')
        asked: list[str] = []

        def fake_is_on_pypi(version: str) -> bool:
            asked.append(version)
            return True

        monkeypatch.setattr(vre_lib_lower_bound, "is_on_pypi", fake_is_on_pypi)
        check_lower_bound_on_pypi(pyproject)
        assert asked == ["0.1.3"]

    def test_fails_if_the_lower_bound_is_not_on_pypi(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1.3,<0.2",')
        monkeypatch.setattr(vre_lib_lower_bound, "is_on_pypi", lambda _: False)
        with pytest.raises(SystemExit, match=r"dsp-vre-lib 0\.1\.3 is not on PyPI"):
            check_lower_bound_on_pypi(pyproject)

    def test_fails_without_lower_bound(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib<0.2",')
        with pytest.raises(SystemExit, match="has no lower bound"):
            check_lower_bound_on_pypi(pyproject)

    def test_passes_without_vre_lib_dependency(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pyproject = _write_pyproject(tmp_path, '"lxml",')
        monkeypatch.setattr(vre_lib_lower_bound, "is_on_pypi", lambda _: pytest.fail("must not ask PyPI"))
        check_lower_bound_on_pypi(pyproject)
