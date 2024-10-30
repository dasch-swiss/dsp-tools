import warnings
from warnings import WarningMessage

import pytest

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.models.migration_metadata import MigrationMetadata


def test_migration_metadata_creation_date_good() -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        MigrationMetadata("2019-01-09T15:45:54.502951Z", None, None, "id")
        assert len(caught_warnings) == 1
        assert isinstance(caught_warnings[0], WarningMessage)


def test_migration_metadata_iri_good() -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        MigrationMetadata(None, "http://rdfh.ch/4123/TqAnYQzrSzC2ctT06OJMYB", None, "id")
        assert len(caught_warnings) == 1
        assert isinstance(caught_warnings[0], WarningMessage)


def test_migration_metadata_ark_good() -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        MigrationMetadata(None, None, "ark:/72163/4123-43xc6ivb931-a.2022829", "id")
        assert len(caught_warnings) == 1
        assert isinstance(caught_warnings[0], WarningMessage)


def test_migration_metadata_creation_date_warns() -> None:
    with pytest.warns((DspToolsUserWarning, DeprecationWarning)):
        MigrationMetadata("2019-01-054.502951Z", None, None, "id")


def test_migration_metadata_iri_warns() -> None:
    with pytest.warns((DspToolsUserWarning, DeprecationWarning)):
        MigrationMetadata(None, "http:123/TqAnYQzrSzC2ctT06OJMYB", None, "id")


def test_migration_metadata_ark_warns() -> None:
    with pytest.warns((DspToolsUserWarning, DeprecationWarning)):
        MigrationMetadata(None, None, "163/4123-43xc6ivb931-a.2022829", "id")


def test_migration_metadata_as_attrib_empty() -> None:
    with pytest.warns((DspToolsUserWarning, DeprecationWarning)):
        result = MigrationMetadata(None, None, None, "id").as_attrib()
    assert not result


if __name__ == "__main__":
    pytest.main([__file__])
