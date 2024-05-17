from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.commands.xmlupload.upload_config import UploadConfig


def test_invalid_arguments() -> None:
    """Test the 'dsp-tools' command with invalid arguments"""
    args = "invalid".split()
    with pytest.raises(SystemExit) as ex:
        entry_point.run(args)
    assert ex.value.code == 2


@patch("dsp_tools.cli.call_action.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only --validate-only' command"""
    file = "filename.json"
    args = f"create --lists-only --validate-only {file}".split()
    entry_point.run(args)
    validate_lists.assert_called_once_with(file)


@patch("dsp_tools.cli.call_action.create_lists")
def test_lists_create(create_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only' command"""
    create_lists.return_value = ({}, True)
    file = "filename.json"
    args = f"create --lists-only {file}".split()
    entry_point.run(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
    )


@patch("dsp_tools.cli.call_action.validate_project")
def test_project_validate(validate_project: Mock) -> None:
    """Test the 'dsp-tools create --validate-only' command"""
    file = "filename.json"
    args = f"create --validate-only {file}".split()
    entry_point.run(args)
    validate_project.assert_called_once_with(file)


@patch("dsp_tools.cli.call_action.create_project")
def test_project_create(create_project: Mock) -> None:
    """Test the 'dsp-tools create' command"""
    file = "filename.json"
    args = f"create {file}".split()
    entry_point.run(args)
    create_project.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user_mail="root@example.com",
        password="test",
        verbose=False,
    )


@patch("dsp_tools.cli.call_action.get_project")
def test_project_get(get_project: Mock) -> None:
    """Test the 'dsp-tools get --project' command"""
    file = "filename.json"
    project = "shortname"
    args = f"get --project {project} {file}".split()
    entry_point.run(args)
    get_project.assert_called_once_with(
        project_identifier=project,
        outfile_path=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        verbose=False,
    )


@patch("dsp_tools.cli.call_action.validate_xml")
def test_xmlupload_validate(validate_xml: Mock) -> None:
    """Test the 'dsp-tools xmlupload --validate-only' command"""
    file = "filename.xml"
    args = f"xmlupload --validate-only {file}".split()
    entry_point.run(args)
    validate_xml.assert_called_once_with(file)


@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload(xmlupload: Mock) -> None:
    """Test the 'dsp-tools xmlupload' command"""
    file = "filename.xml"
    args = f"xmlupload {file}".split()
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        imgdir=".",
        dsp_ingest_url="http://0.0.0.0:3340",
        config=UploadConfig(),
    )


@patch("dsp_tools.cli.call_action.excel2json")
def test_excel2json(excel2json: Mock) -> None:
    """Test the 'dsp-tools excel2json' command"""
    folder = "folder"
    out_file = "filename.json"
    args = f"excel2json {folder} {out_file}".split()
    entry_point.run(args)
    excel2json.assert_called_once_with(
        data_model_files=folder,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.excel2lists")
def test_excel2lists(excel2lists: Mock) -> None:
    """Test the 'dsp-tools excel2lists' command"""
    excel2lists.return_value = ([], True)
    file = "filename.xlsx"
    out_file = "filename.json"
    args = f"excel2lists {file} {out_file}".split()
    entry_point.run(args)
    excel2lists.assert_called_once_with(
        excelfolder=file,
        path_to_output_file=out_file,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action.excel2resources")
def test_excel2resources(excel2resources: Mock) -> None:
    """Test the 'dsp-tools excel2resources' command"""
    excel2resources.return_value = ([], True)
    file = "filename.xlsx"
    out_file = "filename.json"
    args = f"excel2resources {file} {out_file}".split()
    entry_point.run(args)
    excel2resources.assert_called_once_with(
        excelfile=file,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.excel2properties")
def test_excel2properties(excel2properties: Mock) -> None:
    """Test the 'dsp-tools excel2properties' command"""
    excel2properties.return_value = ([], True)
    file = "filename.xlsx"
    out_file = "filename.json"
    args = f"excel2properties {file} {out_file}".split()
    entry_point.run(args)
    excel2properties.assert_called_once_with(
        excelfile=file,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.id2iri")
def test_id2iri(id2iri: Mock) -> None:
    """Test the 'dsp-tools id2iri' command"""
    xml_file = "filename.xml"
    json_file = "filename.json"
    args = f"id2iri {xml_file} {json_file}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=xml_file,
        json_file=json_file,
        remove_resource_if_id_in_mapping=False,
    )


@patch("dsp_tools.cli.call_action.excel2xml", return_value=("foo", "bar"))
def test_excel2xml(excel2xml: Mock) -> None:
    """Test the 'dsp-tools excel2xml' command"""
    excel_file = "filename.xlsx"
    shortcode = "1234"
    onto = "someonto"
    args = f"excel2xml {excel_file} {shortcode} {onto}".split()
    entry_point.run(args)
    excel2xml.assert_called_once_with(
        datafile=excel_file,
        shortcode=shortcode,
        default_ontology=onto,
    )


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
def test_start_stack(start_stack: Mock) -> None:
    """Test the 'dsp-tools start-stack' command"""
    args = "start-stack".split()
    entry_point.run(args)
    start_stack.assert_called_once_with()


@patch("dsp_tools.commands.start_stack.StackHandler.stop_stack")
def test_stop_stack(stop_stack: Mock) -> None:
    """Test the 'dsp-tools stop-stack' command"""
    args = "stop-stack".split()
    entry_point.run(args)
    stop_stack.assert_called_once_with()


@patch("dsp_tools.cli.call_action.generate_template_repo")
def test_template(generate_template_repo: Mock) -> None:
    """Test the 'dsp-tools template' command"""
    args = "template".split()
    entry_point.run(args)
    generate_template_repo.assert_called_once_with()


@patch("dsp_tools.cli.call_action.upload_rosetta")
def test_rosetta(upload_rosetta: Mock) -> None:
    """Test the 'dsp-tools rosetta' command"""
    args = "rosetta".split()
    entry_point.run(args)
    upload_rosetta.assert_called_once_with()


if __name__ == "__main__":
    pytest.main([__file__])
