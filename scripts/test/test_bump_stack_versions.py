from pathlib import Path

import pytest

from scripts.bump_stack_versions import _get_versions_from_env
from scripts.bump_stack_versions import _parse_pr_url
from scripts.bump_stack_versions import _require_env
from scripts.bump_stack_versions import _write_github_output


class TestRequireEnv:
    def test_returns_value_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SOME_VAR", "some_value")
        assert _require_env("SOME_VAR") == "some_value"

    def test_exits_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SOME_VAR", raising=False)
        with pytest.raises(SystemExit):
            _require_env("SOME_VAR")

    def test_exits_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SOME_VAR", "")
        with pytest.raises(SystemExit):
            _require_env("SOME_VAR")


class TestGetVersionsFromEnv:
    def test_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RELEASE", "2026.03.04")
        monkeypatch.setenv("API", "v35.3.0")
        monkeypatch.setenv("APP", "v12.10.0")
        monkeypatch.setenv("DB", "5.5.0-3")
        key, versions = _get_versions_from_env()
        assert key == "2026.03.04"
        assert versions == {"api": "v35.3.0", "app": "v12.10.0", "db": "5.5.0-3"}

    def test_missing_release_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("RELEASE", raising=False)
        monkeypatch.setenv("API", "v35.3.0")
        monkeypatch.setenv("APP", "v12.10.0")
        monkeypatch.setenv("DB", "5.5.0-3")
        with pytest.raises(SystemExit):
            _get_versions_from_env()

    def test_missing_api_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RELEASE", "2026.03.04")
        monkeypatch.delenv("API", raising=False)
        monkeypatch.setenv("APP", "v12.10.0")
        monkeypatch.setenv("DB", "5.5.0-3")
        with pytest.raises(SystemExit):
            _get_versions_from_env()

    def test_missing_app_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RELEASE", "2026.03.04")
        monkeypatch.setenv("API", "v35.3.0")
        monkeypatch.delenv("APP", raising=False)
        monkeypatch.setenv("DB", "5.5.0-3")
        with pytest.raises(SystemExit):
            _get_versions_from_env()

    def test_missing_db_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RELEASE", "2026.03.04")
        monkeypatch.setenv("API", "v35.3.0")
        monkeypatch.setenv("APP", "v12.10.0")
        monkeypatch.delenv("DB", raising=False)
        with pytest.raises(SystemExit):
            _get_versions_from_env()

    def test_malformed_release_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RELEASE", "2026.3.4")
        monkeypatch.setenv("API", "v35.3.0")
        monkeypatch.setenv("APP", "v12.10.0")
        monkeypatch.setenv("DB", "5.5.0-3")
        with pytest.raises(SystemExit):
            _get_versions_from_env()


class TestParsePrUrl:
    def test_takes_the_url_from_the_last_line(self) -> None:
        stdout = "Warning: 1 uncommitted change\nhttps://github.com/dasch-swiss/dsp-tools/pull/2392\n"
        assert _parse_pr_url(stdout) == "https://github.com/dasch-swiss/dsp-tools/pull/2392"

    def test_exits_when_no_url(self) -> None:
        with pytest.raises(SystemExit):
            _parse_pr_url("Creating pull request for chore/bump-version-2026.03.04 into main\n")

    def test_exits_when_empty(self) -> None:
        with pytest.raises(SystemExit):
            _parse_pr_url("")


class TestWriteGithubOutput:
    def test_appends_key_value(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        output_file = tmp_path / "github_output"
        output_file.write_text("existing=value\n", encoding="utf-8")
        monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))
        _write_github_output("pr_url", "https://github.com/dasch-swiss/dsp-tools/pull/2392")
        expected = "existing=value\npr_url=https://github.com/dasch-swiss/dsp-tools/pull/2392\n"
        assert output_file.read_text(encoding="utf-8") == expected

    def test_is_a_no_op_outside_github_actions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
        _write_github_output("pr_url", "https://github.com/dasch-swiss/dsp-tools/pull/2392")
