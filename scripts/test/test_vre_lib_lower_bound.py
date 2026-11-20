import io
import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from scripts import vre_lib_lower_bound
from scripts.vre_lib_lower_bound import check_lower_bound_on_pypi
from scripts.vre_lib_lower_bound import is_on_pypi
from scripts.vre_lib_lower_bound import main
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

    def test_normalizes_the_version(self) -> None:
        assert raise_lower_bound("dsp-vre-lib>=0.1,<0.2", "v0.1.3") == "dsp-vre-lib<0.2,>=0.1.3"

    def test_keeps_extras_and_markers(self) -> None:
        raised = raise_lower_bound('dsp-vre-lib[x]>=0.1,<0.2; python_version >= "3.12"', "0.1.3")
        assert raised == 'dsp-vre-lib[x]<0.2,>=0.1.3; python_version >= "3.12"'

    @pytest.mark.parametrize("dependency", ["dsp-vre-lib~=0.1.2", "dsp-vre-lib==0.1.2", "dsp-vre-lib>0.1,<0.2"])
    def test_fails_on_other_operators(self, dependency: str) -> None:
        with pytest.raises(ValueError, match="Use the form"):
            raise_lower_bound(dependency, "0.1.3")


class TestRaiseLowerBoundInPyproject:
    def test_changes_only_the_vre_lib_line(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2",  # keep this comment')
        raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        expected = PYPROJECT_TEMPLATE.format(vre_lib='"dsp-vre-lib<0.2,>=0.1.3",  # keep this comment')
        assert pyproject.read_text(encoding="utf-8") == expected

    @pytest.mark.parametrize("name", ["dsp_vre_lib", "DSP-VRE-Lib"])
    def test_finds_the_name_in_other_spellings(self, tmp_path: Path, name: str) -> None:
        pyproject = _write_pyproject(tmp_path, f'"{name}>=0.1,<0.2",')
        raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        assert f'"{name}<0.2,>=0.1.3",' in pyproject.read_text(encoding="utf-8")

    def test_ignores_a_similar_name(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib-extra>=0.1,<0.2",')
        before = pyproject.read_text(encoding="utf-8")
        raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        assert pyproject.read_text(encoding="utf-8") == before

    def test_fails_if_the_text_of_the_dependency_is_not_found(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2; python_version >= \\"3.12\\"",')
        before = pyproject.read_text(encoding="utf-8")
        with pytest.raises(SystemExit, match="Change the dependency by hand"):
            raise_lower_bound_in_pyproject(pyproject, "0.1.3")
        assert pyproject.read_text(encoding="utf-8") == before

    def test_fails_on_two_vre_lib_dependencies(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2",\n    "dsp_vre_lib>=0.1,<0.2",')
        with pytest.raises(SystemExit, match="more than one"):
            raise_lower_bound_in_pyproject(pyproject, "0.1.3")

    def test_no_change_if_the_upper_bound_fails(self, tmp_path: Path) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2",')
        before = pyproject.read_text(encoding="utf-8")
        with pytest.raises(ValueError, match="does not satisfy"):
            raise_lower_bound_in_pyproject(pyproject, "0.2.0")
        assert pyproject.read_text(encoding="utf-8") == before

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


class _FakeResponse(io.BytesIO):
    status = 200


def _patch_urlopen(monkeypatch: pytest.MonkeyPatch, result: dict[str, object] | urllib.error.HTTPError) -> None:
    def fake_urlopen(url: str, timeout: int) -> _FakeResponse:  # noqa: ARG001
        if isinstance(result, urllib.error.HTTPError):
            raise result
        return _FakeResponse(json.dumps(result).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://pypi.org", code, "error", {}, None)  # type: ignore[arg-type]


class TestIsOnPypi:
    def test_released_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_urlopen(monkeypatch, {"info": {"yanked": False}})
        assert is_on_pypi("0.1.3")

    def test_yanked_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_urlopen(monkeypatch, {"info": {"yanked": True}})
        assert not is_on_pypi("0.1.3")

    def test_unknown_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_urlopen(monkeypatch, _http_error(404))
        assert not is_on_pypi("0.1.3")

    def test_server_error_is_raised(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_urlopen(monkeypatch, _http_error(500))
        with pytest.raises(urllib.error.HTTPError):
            is_on_pypi("0.1.3")


class TestMain:
    def test_raise(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1,<0.2",')
        monkeypatch.setattr(vre_lib_lower_bound, "PYPROJECT_PATH", pyproject)
        monkeypatch.setattr("sys.argv", ["vre_lib_lower_bound.py", "raise", "0.1.3"])
        main()
        assert '"dsp-vre-lib<0.2,>=0.1.3",' in pyproject.read_text(encoding="utf-8")

    def test_check_on_pypi(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pyproject = _write_pyproject(tmp_path, '"dsp-vre-lib>=0.1.3,<0.2",')
        monkeypatch.setattr(vre_lib_lower_bound, "PYPROJECT_PATH", pyproject)
        monkeypatch.setattr(vre_lib_lower_bound, "is_on_pypi", lambda _: False)
        monkeypatch.setattr("sys.argv", ["vre_lib_lower_bound.py", "check-on-pypi"])
        with pytest.raises(SystemExit, match="is not on PyPI"):
            main()

    @pytest.mark.parametrize("args", [[], ["raise"], ["unknown"]])
    def test_usage_error(self, monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
        monkeypatch.setattr("sys.argv", ["vre_lib_lower_bound.py", *args])
        with pytest.raises(SystemExit, match="usage"):
            main()
