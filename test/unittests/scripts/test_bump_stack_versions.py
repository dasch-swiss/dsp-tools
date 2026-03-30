import pytest

from scripts.bump_stack_versions import _get_versions_from_env
from scripts.bump_stack_versions import _update_compose_content

COMPOSE_FIXTURE = """\
---
services:
  api:
    image: daschswiss/knora-api:v35.2.0
    depends_on:
      - sipi
      - db

  sipi:
    image: daschswiss/knora-sipi:v35.2.0

  ingest:
    image: daschswiss/dsp-ingest:v35.2.0

  app:
    image: daschswiss/dsp-app:v12.9.0

  db:
    image: daschswiss/apache-jena-fuseki:5.5.0-3
"""


class TestGetVersionsFromEnv:
    def test_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VERSION_JSON", '{"release":"2026.03.04","api":"v35.3.0","app":"v12.10.0","db":"5.5.0-3"}')
        key, versions = _get_versions_from_env()
        assert key == "2026.03.04"
        assert versions == {"api": "v35.3.0", "app": "v12.10.0", "db": "5.5.0-3"}

    def test_malformed_json_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VERSION_JSON", "not-valid-json")
        with pytest.raises(SystemExit):
            _get_versions_from_env()


class TestUpdateComposeContent:
    def test_api_version_updated(self) -> None:
        versions = {"api": "v35.3.0", "app": "v12.9.0", "db": "5.5.0-3"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/knora-api:v35.3.0" in result

    def test_sipi_version_updated_with_api_version(self) -> None:
        versions = {"api": "v35.3.0", "app": "v12.9.0", "db": "5.5.0-3"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/knora-sipi:v35.3.0" in result

    def test_ingest_version_updated_with_api_version(self) -> None:
        versions = {"api": "v35.3.0", "app": "v12.9.0", "db": "5.5.0-3"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/dsp-ingest:v35.3.0" in result

    def test_app_version_updated_independently(self) -> None:
        versions = {"api": "v35.2.0", "app": "v12.10.0", "db": "5.5.0-3"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/dsp-app:v12.10.0" in result
        assert "daschswiss/knora-api:v35.2.0" in result

    def test_db_version_updated_without_v_prefix(self) -> None:
        versions = {"api": "v35.2.0", "app": "v12.9.0", "db": "5.6.0-1"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/apache-jena-fuseki:5.6.0-1" in result

    def test_no_change_when_versions_already_current(self) -> None:
        versions = {"api": "v35.2.0", "app": "v12.9.0", "db": "5.5.0-3"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert result == COMPOSE_FIXTURE

    def test_all_services_updated_together(self) -> None:
        versions = {"api": "v36.0.0", "app": "v13.0.0", "db": "6.0.0-1"}
        result = _update_compose_content(COMPOSE_FIXTURE, versions)
        assert "daschswiss/knora-api:v36.0.0" in result
        assert "daschswiss/knora-sipi:v36.0.0" in result
        assert "daschswiss/dsp-ingest:v36.0.0" in result
        assert "daschswiss/dsp-app:v13.0.0" in result
        assert "daschswiss/apache-jena-fuseki:6.0.0-1" in result
