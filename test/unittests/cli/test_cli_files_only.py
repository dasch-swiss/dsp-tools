from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.commands.excel2json.models.json_header import PermissionsOverrulesUnprefixed

ID_2_IRI_JSON_PATH = "testdata/id2iri/test-id2iri-mapping.json"
DATA_XML_PATH = "testdata/xml-data/test-data-systematic-4123.xml"
EXCEL_FOLDER = "testdata/excel2json/excel2json_files"
EXCEL_FILE_PATH = "testdata/excel2json/excel2json_files/lists/list3.xlsx"


@patch("dsp_tools.cli.call_action_files_only.excel2json")
def test_excel2json(excel2json: Mock) -> None:
    out_file = f"{EXCEL_FOLDER}/filename.json"
    args = f"excel2json {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    excel2json.assert_called_once_with(
        data_model_files=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action_files_only.excel2lists")
def test_excel2lists(excel2lists: Mock) -> None:
    excel2lists.return_value = ([], True)
    out_file = "filename.json"
    args = f"excel2lists {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    excel2lists.assert_called_once_with(
        excelfolder=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action_files_only.excel2resources")
def test_excel2resources(excel2resources: Mock) -> None:
    excel2resources.return_value = ([], PermissionsOverrulesUnprefixed([], []), True)
    out_file = "filename.json"
    args = f"excel2resources {EXCEL_FILE_PATH} {out_file}".split()
    entry_point.run(args)
    excel2resources.assert_called_once_with(
        excelfile=EXCEL_FILE_PATH,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action_files_only.excel2properties")
def test_excel2properties(excel2properties: Mock) -> None:
    excel2properties.return_value = ([], PermissionsOverrulesUnprefixed([], []), True)
    out_file = "filename.json"
    args = f"excel2properties {EXCEL_FILE_PATH} {out_file}".split()
    entry_point.run(args)
    excel2properties.assert_called_once_with(
        excelfile=EXCEL_FILE_PATH,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action_files_only.old_excel2json")
def test_old_excel2json(old_excel2json: Mock) -> None:
    out_file = "filename.json"
    args = f"old-excel2json {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    old_excel2json.assert_called_once_with(
        data_model_files=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action_files_only.old_excel2lists")
def test_old_excel2lists(old_excel2lists: Mock) -> None:
    old_excel2lists.return_value = ([], True)
    out_file = "filename.json"
    args = f"old-excel2lists {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    old_excel2lists.assert_called_once_with(
        excelfolder=EXCEL_FOLDER,
        path_to_output_file=out_file,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action_files_only.id2iri")
def test_id2iri_default(id2iri: Mock) -> None:
    args = f"id2iri {DATA_XML_PATH} {ID_2_IRI_JSON_PATH}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=DATA_XML_PATH,
        json_file=ID_2_IRI_JSON_PATH,
        remove_resource_if_id_in_mapping=False,
    )


@patch("dsp_tools.cli.call_action_files_only.id2iri")
def test_id2iri_remove_resources(id2iri: Mock) -> None:
    args = f"id2iri --remove-resources {DATA_XML_PATH} {ID_2_IRI_JSON_PATH}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=DATA_XML_PATH,
        json_file=ID_2_IRI_JSON_PATH,
        remove_resource_if_id_in_mapping=True,
    )


if __name__ == "__main__":
    pytest.main([__file__])
