from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.start_stack import StackConfiguration
from dsp_tools.commands.xmlupload.upload_config import UploadConfig

EXIT_CODE_TWO = 2


def test_invalid_arguments() -> None:
    args = "invalid".split()
    with pytest.raises(SystemExit) as ex:
        entry_point.run(args)
    assert ex.value.code == EXIT_CODE_TWO


@patch("dsp_tools.cli.call_action.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock) -> None:
    file = "filename.json"
    args = f"create --lists-only --validate-only {file}".split()
    entry_point.run(args)
    validate_lists.assert_called_once_with(file)


@patch("dsp_tools.cli.call_action.create_lists")
def test_lists_create(create_lists: Mock) -> None:
    create_lists.return_value = ({}, True)
    file = "filename.json"
    args = f"create --lists-only {file}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        creds=creds,
    )


@patch("dsp_tools.cli.call_action.validate_project")
def test_project_validate(validate_project: Mock) -> None:
    file = "filename.json"
    args = f"create --validate-only {file}".split()
    entry_point.run(args)
    validate_project.assert_called_once_with(file)


@patch("dsp_tools.cli.call_action.create_project")
def test_project_create(create_project: Mock) -> None:
    file = "filename.json"
    args = f"create {file}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    create_project.assert_called_once_with(
        project_file_as_path_or_parsed=file,
        creds=creds,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action.get_project")
def test_project_get(get_project: Mock) -> None:
    file = "filename.json"
    project = "shortname"
    args = f"get --project {project} {file}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    get_project.assert_called_once_with(
        project_identifier=project,
        outfile_path=file,
        creds=creds,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_default(xmlupload: Mock) -> None:
    file = "filename.xml"
    args = f"xmlupload {file}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(file),
        creds=creds,
        imgdir=".",
        config=UploadConfig(skip_iiif_validation=False, interrupt_after=None),
    )


@patch("dsp_tools.cli.call_action.validate_xml_file")
def test_xmlupload_validate(validate_xml: Mock) -> None:
    file = "filename.xml"
    args = f"xmlupload --validate-only {file}".split()
    entry_point.run(args)
    validate_xml.assert_called_once_with(Path(file))


@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_no_iiif(xmlupload: Mock) -> None:
    file = "filename.xml"
    no_validation = "--no-iiif-uri-validation"
    args = f"xmlupload {no_validation} {file}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(file),
        creds=creds,
        imgdir=".",
        config=UploadConfig(skip_iiif_validation=True),
    )


@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_interrupt_after(xmlupload: Mock) -> None:
    file = "filename.xml"
    args = f"xmlupload --interrupt-after=1 {file}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(file), creds=creds, imgdir=".", config=UploadConfig(interrupt_after=1)
    )


@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_default(validate_data: Mock) -> None:
    file = "filename.xml"
    args = f"validate-data {file}".split()
    entry_point.run(args)
    validate_data.assert_called_once_with(
        filepath=Path(file), api_url="http://0.0.0.0:3333", dev_route=False, save_graphs=False
    )


@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_dev(validate_data: Mock) -> None:
    file = "filename.xml"
    args = f"validate-data {file} --dev".split()
    entry_point.run(args)
    validate_data.assert_called_once_with(
        filepath=Path(file), api_url="http://0.0.0.0:3333", dev_route=True, save_graphs=False
    )


@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_save_graph(validate_data: Mock) -> None:
    file = "filename.xml"
    args = f"validate-data {file} --save-graphs".split()
    entry_point.run(args)
    validate_data.assert_called_once_with(
        filepath=Path(file), api_url="http://0.0.0.0:3333", dev_route=False, save_graphs=True
    )


@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_other_server(validate_data: Mock) -> None:
    file = "filename.xml"
    args = f"validate-data {file} -s https://api.dasch.swiss".split()
    entry_point.run(args)
    validate_data.assert_called_once_with(
        filepath=Path(file), api_url="https://api.dasch.swiss", dev_route=False, save_graphs=False
    )


@patch("dsp_tools.cli.call_action.resume_xmlupload")
def test_resume_xmlupload_default(resume_xmlupload: Mock) -> None:
    args = "resume-xmlupload".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=False)


@patch("dsp_tools.cli.call_action.resume_xmlupload")
def test_resume_xmlupload_skip_first_resource(resume_xmlupload: Mock) -> None:
    args = "resume-xmlupload --skip-first-resource".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=True)


@patch("dsp_tools.cli.call_action.upload_files")
def test_upload_files_localhost(upload_files: Mock) -> None:
    file = "filename.xml"
    args = f"upload-files {file}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    upload_files.assert_called_once_with(xml_file=Path(file), creds=creds, imgdir=Path("."))


@patch("dsp_tools.cli.call_action.upload_files")
def test_upload_files_remote(upload_files: Mock) -> None:
    file = "filename.xml"
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"upload-files --server={server} --user {user} --password={password} {file}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server=server,
        user=user,
        password=password,
        dsp_ingest_url=server.replace("api", "ingest"),
    )
    upload_files.assert_called_once_with(xml_file=Path(file), creds=creds, imgdir=Path("."))


@patch("dsp_tools.cli.call_action.ingest_files")
def test_ingest_files_localhost(ingest_files: Mock) -> None:
    shortcode = "1234"
    args = f"ingest-files {shortcode}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_files.assert_called_once_with(creds=creds, shortcode=shortcode)


@patch("dsp_tools.cli.call_action.ingest_files")
def test_ingest_files_remote(ingest_files: Mock) -> None:
    shortcode = "1234"
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"ingest-files --server={server} --user {user} --password={password} {shortcode}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server=server,
        user=user,
        password=password,
        dsp_ingest_url=server.replace("api", "ingest"),
    )
    ingest_files.assert_called_once_with(creds=creds, shortcode=shortcode)


@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_localhost(ingest_xmlupload: Mock) -> None:
    xml_file = Path("filename.xml")
    args = f"ingest-xmlupload {xml_file}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(xml_file=xml_file, creds=creds, interrupt_after=None)


@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_interrupt_after(ingest_xmlupload: Mock) -> None:
    xml_file = Path("filename.xml")
    args = f"ingest-xmlupload --interrupt-after=1 {xml_file}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(xml_file=xml_file, creds=creds, interrupt_after=1)


@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_remote(ingest_xmlupload: Mock) -> None:
    xml_file = Path("filename.xml")
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"ingest-xmlupload --server={server} --user {user} --password={password} {xml_file}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server=server,
        user=user,
        password=password,
        dsp_ingest_url=server.replace("api", "ingest"),
    )
    ingest_xmlupload.assert_called_once_with(xml_file=xml_file, creds=creds, interrupt_after=None)


@patch("dsp_tools.cli.call_action.excel2json")
def test_excel2json(excel2json: Mock) -> None:
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
    excel2properties.return_value = ([], True)
    file = "filename.xlsx"
    out_file = "filename.json"
    args = f"excel2properties {file} {out_file}".split()
    entry_point.run(args)
    excel2properties.assert_called_once_with(
        excelfile=file,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.new_excel2json")
def test_new_excel2json(new_excel2json: Mock) -> None:
    folder = "folder"
    out_file = "filename.json"
    args = f"new-excel2json {folder} {out_file}".split()
    entry_point.run(args)
    new_excel2json.assert_called_once_with(
        data_model_files=folder,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.new_excel2lists")
def test_new_excel2lists(new_excel2lists: Mock) -> None:
    new_excel2lists.return_value = ([], True)
    file = "filename.xlsx"
    out_file = "filename.json"
    args = f"new-excel2lists {file} {out_file}".split()
    entry_point.run(args)
    new_excel2lists.assert_called_once_with(
        excelfolder=file,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.id2iri")
def test_id2iri_default(id2iri: Mock) -> None:
    xml_file = "filename.xml"
    json_file = "filename.json"
    args = f"id2iri {xml_file} {json_file}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=xml_file,
        json_file=json_file,
        remove_resource_if_id_in_mapping=False,
    )


@patch("dsp_tools.cli.call_action.id2iri")
def test_id2iri_remove_resources(id2iri: Mock) -> None:
    xml_file = "filename.xml"
    json_file = "filename.json"
    args = f"id2iri --remove-resources {xml_file} {json_file}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=xml_file,
        json_file=json_file,
        remove_resource_if_id_in_mapping=True,
    )


@patch("dsp_tools.cli.call_action.excel2xml", return_value=("foo", "bar"))
def test_excel2xml(excel2xml: Mock) -> None:
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
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_default(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=False,
            api_version_for_validate=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_validation(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --validation".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=False,
            api_version_for_validate=True,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_max_file_size(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --max_file_size=1".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=1,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_prune(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --prune".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=True,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_no_prune(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --no-prune".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=True,
            latest_dev_version=False,
            upload_test_data=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_latest(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --latest".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=True,
            upload_test_data=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_with_test_data(mock_init: Mock, start_stack: Mock) -> None:
    args = "start-stack --with-test-data".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=True,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.commands.start_stack.StackHandler.stop_stack")
def test_stop_stack(stop_stack: Mock) -> None:
    args = "stop-stack".split()
    entry_point.run(args)
    stop_stack.assert_called_once_with()


@patch("dsp_tools.cli.call_action.generate_template_repo")
def test_template(generate_template_repo: Mock) -> None:
    args = "template".split()
    entry_point.run(args)
    generate_template_repo.assert_called_once_with()


@patch("dsp_tools.cli.call_action.upload_rosetta")
def test_rosetta(upload_rosetta: Mock) -> None:
    args = "rosetta".split()
    entry_point.run(args)
    upload_rosetta.assert_called_once_with()


@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_flag_absent(check_version: Mock, xmlupload: Mock) -> None:
    args = "xmlupload --user=testuser data.xml".split()
    entry_point.run(args)
    check_version.assert_called_once()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_leftmost(check_version: Mock, xmlupload: Mock) -> None:
    args = "xmlupload --suppress-update-prompt --user=testuser data.xml".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_middle(check_version: Mock, xmlupload: Mock) -> None:
    args = "xmlupload --user=testuser --suppress-update-prompt data.xml".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_rightmost(check_version: Mock, xmlupload: Mock) -> None:
    args = "xmlupload --user=testuser data.xml --suppress-update-prompt".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
