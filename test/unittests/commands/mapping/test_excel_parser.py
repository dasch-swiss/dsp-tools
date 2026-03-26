from pathlib import Path

import pandas as pd
import pytest

from dsp_tools.commands.excel2json.exceptions import InvalidFileFormatError
from dsp_tools.commands.mapping.excel_parser import parse_mapping_excel
from dsp_tools.commands.mapping.models import ClassMapping
from dsp_tools.commands.mapping.models import PropertyMapping


def _write_excel(
    path: Path,
    prefix_data: dict[str, list[str]],
    classes_data: dict[str, list[str]],
    properties_data: dict[str, list[str]],
) -> None:
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(prefix_data).to_excel(writer, sheet_name="prefix", index=False)
        pd.DataFrame(classes_data).to_excel(writer, sheet_name="classes", index=False)
        pd.DataFrame(properties_data).to_excel(writer, sheet_name="properties", index=False)


def test_parse_excel_success(tmp_path: Path) -> None:
    excel_path = tmp_path / "test.xlsx"
    _write_excel(
        excel_path,
        prefix_data={"prefix": ["schema", "ex"], "link": ["http://schema.org/", "http://example.org/"]},
        classes_data={"class": ["Book", "Article"], "mapping": ["schema:Book", "schema:Article; ex:Article"]},
        properties_data={"property": ["title"], "mapping": ["schema:name"]},
    )
    excel, prefix_map = parse_mapping_excel(excel_path)
    assert prefix_map == {"schema": "http://schema.org/", "ex": "http://example.org/"}
    assert len(excel.classes) == 2
    assert excel.classes[0] == ClassMapping(class_iri="Book", mapping_iris=["schema:Book"])
    assert excel.classes[1] == ClassMapping(class_iri="Article", mapping_iris=["schema:Article", "ex:Article"])
    assert len(excel.properties) == 1
    assert excel.properties[0] == PropertyMapping(property_iri="title", mapping_iris=["schema:name"])


def test_missing_sheet_raises(tmp_path: Path) -> None:
    excel_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame({"prefix": ["schema"], "link": ["http://schema.org/"]}).to_excel(
            writer, sheet_name="prefix", index=False
        )
        # classes and properties sheets are missing
    with pytest.raises(InvalidFileFormatError, match="classes"):
        parse_mapping_excel(excel_path)


def test_missing_column_raises(tmp_path: Path) -> None:
    excel_path = tmp_path / "test.xlsx"
    _write_excel(
        excel_path,
        prefix_data={"prefix": ["schema"], "link": ["http://schema.org/"]},
        classes_data={"class": ["Book"]},  # missing "mapping" column
        properties_data={"property": ["title"], "mapping": ["schema:name"]},
    )
    with pytest.raises(InvalidFileFormatError, match="mapping"):
        parse_mapping_excel(excel_path)


def test_empty_rows_dropped(tmp_path: Path) -> None:
    excel_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame({"prefix": ["schema", None], "link": ["http://schema.org/", None]}).to_excel(
            writer, sheet_name="prefix", index=False
        )
        pd.DataFrame({"class": ["Book", None], "mapping": ["schema:Book", None]}).to_excel(
            writer, sheet_name="classes", index=False
        )
        pd.DataFrame({"property": ["title"], "mapping": ["schema:name"]}).to_excel(
            writer, sheet_name="properties", index=False
        )
    excel, prefix_map = parse_mapping_excel(excel_path)
    assert len(prefix_map) == 1
    assert len(excel.classes) == 1
