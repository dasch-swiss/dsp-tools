from unittest.mock import Mock, patch

import pytest

from dsp_tools import cli


# test invalid arguments
def test_invalid_arguments() -> None:
    """Test the 'dsp-tools' command with invalid arguments"""
    args = "invalid".split()
    with pytest.raises(SystemExit) as ex:
        cli.run(args)
    assert ex.value.code == 2


# test lists validate
@patch("dsp_tools.cli.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only --validate-only' command"""
    file = "filename.json"
    args = f"create --lists-only --validate-only {file}".split()
    cli.run(args)
    validate_lists.assert_called_once_with(file)


# test lists create
@patch("dsp_tools.cli.create_lists")
def test_lists_create(create_lists: Mock) -> None:
    """Test the 'dsp-tools create --lists-only' command"""
    create_lists.return_value = ({}, True)
    file = "filename.json"
    args = f"create --lists-only {file}".split()
    cli.run(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dump=False,
    )


# test project validate
@patch("dsp_tools.cli.validate_project")
def test_project_validate(validate_project: Mock) -> None:
    """Test the 'dsp-tools create --validate-only' command"""
    file = "filename.json"
    args = f"create --validate-only {file}".split()
    cli.run(args)
    validate_project.assert_called_once_with(file)


# test project create
@patch("dsp_tools.cli.create_project")
def test_project_create(create_project: Mock) -> None:
    """Test the 'dsp-tools create' command"""
    create_project.return_value = True
    file = "filename.json"
    args = f"create {file}".split()
    cli.run(args)
    create_project.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        server="http://0.0.0.0:3333",
        user_mail="root@example.com",
        password="test",
        verbose=False,
        dump=False,
    )


# test project get
@patch("dsp_tools.cli.get_project")
def test_project_get(get_project: Mock) -> None:
    """Test the 'dsp-tools get --project' command"""
    get_project.return_value = True
    file = "filename.json"
    project = "shortname"
    args = f"get --project {project} {file}".split()
    cli.run(args)
    get_project.assert_called_once_with(
        project_identifier=project,
        outfile_path=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        verbose=False,
        dump=False,
    )


# test xmlupload validate
@patch("dsp_tools.cli.validate_xml_against_schema")
def test_xmlupload_validate(validate_xml: Mock) -> None:
    """Test the 'dsp-tools xmlupload --validate-only' command"""
    file = "filename.xml"
    args = f"xmlupload --validate-only {file}".split()
    cli.run(args)
    validate_xml.assert_called_once_with(file)


# test xmlupload
@patch("dsp_tools.cli.xmlupload")
def test_xmlupload(xmlupload: Mock) -> None:
    """Test the 'dsp-tools xmlupload' command"""
    xmlupload.return_value = True
    file = "filename.xml"
    args = f"xmlupload {file}".split()
    cli.run(args)
    xmlupload.assert_called_once_with(
        input_file=file,
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        imgdir=".",
        sipi="http://0.0.0.0:1024",
        verbose=False,
        dump=False,
        save_metrics=False,
        preprocessing_done=False,
    )


# TODO: id2iri too?


# test process-files
@patch("dsp_tools.cli.process_files")
def test_process_files(process_files: Mock) -> None:
    """Test the 'dsp-tools process-files' command"""
    process_files.return_value = True
    input_dir = "input"
    output_dir = "output"
    nthreads = 12
    file = "filename.xml"
    args = f"process-files --input-dir {input_dir} --output-dir {output_dir} --nthreads {nthreads} {file}".split()
    cli.run(args)
    process_files.assert_called_once_with(
        input_dir=input_dir,
        output_dir=output_dir,
        xml_file=file,
        nthreads=nthreads,
        batch_size=3000,
    )


# test upload-files
@patch("dsp_tools.cli.upload_files")
def test_upload_files(upload_files: Mock) -> None:
    """Test the 'dsp-tools upload-files' command"""
    upload_files.return_value = True
    processed_dir = "processed"
    nthreads = 12
    args = f"upload-files --processed-dir {processed_dir} --nthreads {nthreads}".split()
    cli.run(args)
    upload_files.assert_called_once_with(
        dir_with_processed_files=processed_dir,
        nthreads=nthreads,
        user="root@example.com",
        password="test",
        dsp_url="http://0.0.0.0:3333",
        sipi_url="http://0.0.0.0:1024",
    )


# test fast-xmlupload
@patch("dsp_tools.cli.fast_xmlupload")
def test_fast_xmlupload(fast_xmlupload: Mock) -> None:
    """Test the 'dsp-tools fast-xmlupload' command"""
    fast_xmlupload.return_value = True
    file = "filename.xml"
    args = f"fast-xmlupload {file}".split()
    cli.run(args)
    fast_xmlupload.assert_called_once_with(
        xml_file=file,
        user="root@example.com",
        password="test",
        dsp_url="http://0.0.0.0:3333",
        sipi_url="http://0.0.0.0:1024",
    )
