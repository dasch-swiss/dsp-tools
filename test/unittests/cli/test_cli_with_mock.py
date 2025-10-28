from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import regex
import requests

from dsp_tools.cli import entry_point
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.cli.call_action import _check_api_health
from dsp_tools.commands.excel2json.models.json_header import PermissionsOverrulesUnprefixed
from dsp_tools.commands.start_stack import StackConfiguration
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.exceptions import DspApiNotReachableError

EXIT_CODE_TWO = 2

# ruff: noqa: ARG001 Unused function argument

PROJECT_JSON_PATH = "testdata/json-project/systematic-project-4123.json"
ID_2_IRI_JSON_PATH = "testdata/id2iri/test-id2iri-mapping.json"
DATA_XML_PATH = "testdata/xml-data/test-data-systematic-4123.xml"
EXCEL_FOLDER = "testdata/excel2json/excel2json_files"
EXCEL_FILE_PATH = "testdata/excel2json/excel2json_files/lists/list3.xlsx"


def test_invalid_arguments() -> None:
    args = "invalid".split()
    with pytest.raises(SystemExit) as ex:
        entry_point.run(args)
    assert ex.value.code == EXIT_CODE_TWO


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.validate_lists_section_with_schema")
def test_lists_validate(validate_lists: Mock, check_docker: Mock) -> None:
    args = f"create --lists-only --validate-only {PROJECT_JSON_PATH}".split()
    entry_point.run(args)
    validate_lists.assert_called_once_with(PROJECT_JSON_PATH)


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.create_only_lists")
def test_lists_create(create_lists: Mock, check_docker: Mock) -> None:
    create_lists.return_value = ({}, True)
    args = f"create --lists-only {PROJECT_JSON_PATH}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    create_lists.assert_called_once_with(
        project_file_as_path_or_parsed=PROJECT_JSON_PATH,
        creds=creds,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.validate_project")
def test_project_validate(validate_project: Mock, check_docker: Mock) -> None:
    args = f"create --validate-only {PROJECT_JSON_PATH}".split()
    entry_point.run(args)
    validate_project.assert_called_once_with(PROJECT_JSON_PATH)


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.create_project")
def test_project_create(create_project: Mock, check_docker: Mock) -> None:
    args = f"create {PROJECT_JSON_PATH}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    create_project.assert_called_once_with(
        project_file_as_path_or_parsed=PROJECT_JSON_PATH,
        creds=creds,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.get_project")
def test_project_get(get_project: Mock, check_docker: Mock) -> None:
    project = "shortname"
    args = f"get --project {project} {PROJECT_JSON_PATH}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    get_project.assert_called_once_with(
        project_identifier=project,
        outfile_path=PROJECT_JSON_PATH,
        creds=creds,
        verbose=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_default(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(
            interrupt_after=None,
            skip_iiif_validation=False,
            skip_validation=False,
            skip_ontology_validation=False,
            ignore_duplicate_files_warning=False,
            validation_severity=ValidationSeverity.INFO,
            id2iri_replacement_file=None,
            do_not_request_resource_metadata_from_db=False,
        ),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.parse_and_validate_xml_file")
def test_xmlupload_validate(validate_xml: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --validate-only {DATA_XML_PATH}".split()
    entry_point.run(args)
    validate_xml.assert_called_once_with(Path(DATA_XML_PATH))


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_no_iiif(xmlupload: Mock, check_docker: Mock) -> None:
    no_validation = "--no-iiif-uri-validation"
    args = f"xmlupload {no_validation} {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(skip_iiif_validation=True),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_skip_validation(xmlupload: Mock, check_docker: Mock) -> None:
    no_validation = "--skip-validation"
    args = f"xmlupload {no_validation} {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(skip_validation=True),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_ignore_duplicate_files_warning(xmlupload: Mock, check_docker: Mock) -> None:
    ignore_duplicate_files = "--ignore-duplicate-files-warning"
    args = f"xmlupload {ignore_duplicate_files} {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(ignore_duplicate_files_warning=True),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_default_validation_severity_warning(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload {DATA_XML_PATH} --validation-severity warning".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(
            skip_iiif_validation=False,
            interrupt_after=None,
            validation_severity=ValidationSeverity.WARNING,
        ),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_default_validation_severity_error(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload {DATA_XML_PATH} --validation-severity error".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(
            skip_iiif_validation=False,
            interrupt_after=None,
            validation_severity=ValidationSeverity.ERROR,
        ),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_skip_ontology_validation(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload {DATA_XML_PATH} --skip-ontology-validation".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(
            skip_iiif_validation=False,
            interrupt_after=None,
            validation_severity=ValidationSeverity.INFO,
            skip_ontology_validation=True,
        ),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_interrupt_after(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --interrupt-after=1 {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH), creds=creds, imgdir=".", config=UploadConfig(interrupt_after=1)
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_id2iri_replacement_with_file(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --id2iri-replacement-with-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(id2iri_replacement_file=ID_2_IRI_JSON_PATH),
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_default(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_ignore_duplicate_files(validate_data: Mock, check_docker: Mock) -> None:
    ignore_duplicate_files = "--ignore-duplicate-files-warning"
    args = f"validate-data {ignore_duplicate_files} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=True,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_save_graph(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data {DATA_XML_PATH} --save-graphs".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=True,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_other_server(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data {DATA_XML_PATH} -s https://api.dasch.swiss".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com",
        password="test",
        server="https://api.dasch.swiss",
        dsp_ingest_url="https://ingest.dasch.swiss",
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_other_creds(validate_data: Mock, check_docker: Mock) -> None:
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"validate-data {DATA_XML_PATH} --server={server} --user {user} --password={password}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user=user, password=password, server=server, dsp_ingest_url="https://ingest.test.dasch.swiss"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_skip_ontology_validation(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data {DATA_XML_PATH} --skip-ontology-validation".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=True,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_id2iri_replacement_with_file(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data --id2iri-replacement-with-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=ID_2_IRI_JSON_PATH,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.validate_data")
def test_validate_data_do_not_request_resource_metadata_from_db(validate_data: Mock, check_docker: Mock) -> None:
    args = f"validate-data {DATA_XML_PATH} --do-not-request-resource-metadata-from-db".split()
    entry_point.run(args)
    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    validate_data.assert_called_once_with(
        filepath=Path(DATA_XML_PATH),
        save_graphs=False,
        creds=creds,
        ignore_duplicate_files_warning=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=True,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.resume_xmlupload")
def test_resume_xmlupload_default(resume_xmlupload: Mock, check_docker: Mock) -> None:
    args = "resume-xmlupload".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=False)


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.resume_xmlupload")
def test_resume_xmlupload_skip_first_resource(resume_xmlupload: Mock, check_docker: Mock) -> None:
    args = "resume-xmlupload --skip-first-resource".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=True)


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.upload_files")
def test_upload_files_localhost(upload_files: Mock, check_docker: Mock) -> None:
    args = f"upload-files {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    upload_files.assert_called_once_with(xml_file=Path(DATA_XML_PATH), creds=creds, imgdir=Path("."))


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.upload_files")
def test_upload_files_remote(upload_files: Mock, check_docker: Mock) -> None:
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"upload-files --server={server} --user {user} --password={password} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server=server,
        user=user,
        password=password,
        dsp_ingest_url=server.replace("api", "ingest"),
    )
    upload_files.assert_called_once_with(xml_file=Path(DATA_XML_PATH), creds=creds, imgdir=Path("."))


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.ingest_files")
def test_ingest_files_localhost(ingest_files: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_health_with_docker_on_localhost")
@patch("dsp_tools.cli.call_action.ingest_files")
def test_ingest_files_remote(ingest_files: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_localhost(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    args = f"ingest-xmlupload {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=Path(DATA_XML_PATH),
        creds=creds,
        interrupt_after=None,
        skip_validation=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_skip_validation(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    skip_validation = "--skip-validation"
    args = f"ingest-xmlupload {skip_validation} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=Path(DATA_XML_PATH),
        creds=creds,
        interrupt_after=None,
        skip_validation=True,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_interrupt_after(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    args = f"ingest-xmlupload --interrupt-after=1 {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=Path(DATA_XML_PATH),
        creds=creds,
        interrupt_after=1,
        skip_validation=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_remote(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    server = "https://api.test.dasch.swiss"
    user = "first-name.second-name@dasch.swiss"
    password = "foobar"
    args = f"ingest-xmlupload --server={server} --user {user} --password={password} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server=server,
        user=user,
        password=password,
        dsp_ingest_url=server.replace("api", "ingest"),
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=Path(DATA_XML_PATH),
        creds=creds,
        interrupt_after=None,
        skip_validation=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_id2iri_replacement_with_file(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    args = f"ingest-xmlupload --id2iri-replacement-with-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=Path(DATA_XML_PATH),
        creds=creds,
        interrupt_after=None,
        skip_validation=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=ID_2_IRI_JSON_PATH,
        do_not_request_resource_metadata_from_db=False,
    )


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.ingest_xmlupload")
def test_ingest_xmlupload_do_not_request_resource_metadata_from_db(ingest_xmlupload: Mock, check_docker: Mock) -> None:
    args = f"ingest-xmlupload {DATA_XML_PATH} --do-not-request-resource-metadata-from-db".split()
    entry_point.run(args)
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    ingest_xmlupload.assert_called_once_with(
        xml_file=DATA_XML_PATH,
        creds=creds,
        interrupt_after=None,
        skip_validation=False,
        skip_ontology_validation=False,
        id2iri_replacement_file=None,
        do_not_request_resource_metadata_from_db=True,
    )


@patch("dsp_tools.cli.call_action.excel2json")
def test_excel2json(excel2json: Mock) -> None:
    out_file = f"{EXCEL_FOLDER}/filename.json"
    args = f"excel2json {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    excel2json.assert_called_once_with(
        data_model_files=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.excel2lists")
def test_excel2lists(excel2lists: Mock) -> None:
    excel2lists.return_value = ([], True)
    out_file = "filename.json"
    args = f"excel2lists {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    excel2lists.assert_called_once_with(
        excelfolder=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.excel2resources")
def test_excel2resources(excel2resources: Mock) -> None:
    excel2resources.return_value = ([], PermissionsOverrulesUnprefixed([], []), True)
    out_file = "filename.json"
    args = f"excel2resources {EXCEL_FILE_PATH} {out_file}".split()
    entry_point.run(args)
    excel2resources.assert_called_once_with(
        excelfile=EXCEL_FILE_PATH,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.excel2properties")
def test_excel2properties(excel2properties: Mock) -> None:
    excel2properties.return_value = ([], PermissionsOverrulesUnprefixed([], []), True)
    out_file = "filename.json"
    args = f"excel2properties {EXCEL_FILE_PATH} {out_file}".split()
    entry_point.run(args)
    excel2properties.assert_called_once_with(
        excelfile=EXCEL_FILE_PATH,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.old_excel2json")
def test_old_excel2json(old_excel2json: Mock) -> None:
    out_file = "filename.json"
    args = f"old-excel2json {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    old_excel2json.assert_called_once_with(
        data_model_files=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )


@patch("dsp_tools.cli.call_action.old_excel2lists")
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


@patch("dsp_tools.cli.call_action.id2iri")
def test_id2iri_default(id2iri: Mock) -> None:
    args = f"id2iri {DATA_XML_PATH} {ID_2_IRI_JSON_PATH}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=DATA_XML_PATH,
        json_file=ID_2_IRI_JSON_PATH,
        remove_resource_if_id_in_mapping=False,
    )


@patch("dsp_tools.cli.call_action.id2iri")
def test_id2iri_remove_resources(id2iri: Mock) -> None:
    args = f"id2iri --remove-resources {DATA_XML_PATH} {ID_2_IRI_JSON_PATH}".split()
    entry_point.run(args)
    id2iri.assert_called_once_with(
        xml_file=DATA_XML_PATH,
        json_file=ID_2_IRI_JSON_PATH,
        remove_resource_if_id_in_mapping=True,
    )


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_default(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
    args = "start-stack".split()
    entry_point.run(args)
    mock_init.assert_called_once_with(
        StackConfiguration(
            max_file_size=None,
            enforce_docker_system_prune=False,
            suppress_docker_system_prune=False,
            latest_dev_version=False,
            upload_test_data=False,
        )
    )
    start_stack.assert_called_once()


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_max_file_size(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_prune(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_no_prune(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_latest(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_docker_health")
@patch("dsp_tools.commands.start_stack.StackHandler.start_stack")
@patch("dsp_tools.commands.start_stack.StackHandler.__init__", return_value=None)
def test_start_stack_with_test_data(mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_flag_absent(check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --user=testuser {DATA_XML_PATH}".split()
    entry_point.run(args)
    check_version.assert_called_once()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_leftmost(check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --suppress-update-prompt --user=testuser {DATA_XML_PATH}".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_middle(check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --user=testuser --suppress-update-prompt {DATA_XML_PATH}".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
@patch("dsp_tools.cli.entry_point._check_version")
def test_suppress_update_prompt_rightmost(check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload --user=testuser {DATA_XML_PATH} --suppress-update-prompt".split()
    entry_point.run(args)
    check_version.assert_not_called()
    xmlupload.assert_called_once()


@patch("dsp_tools.cli.call_action._check_health_with_docker")
@patch("dsp_tools.cli.call_action.xmlupload")
def test_xmlupload_do_not_request_resource_metadata_from_db(xmlupload: Mock, check_docker: Mock) -> None:
    args = f"xmlupload {DATA_XML_PATH} --do-not-request-resource-metadata-from-db".split()
    creds = ServerCredentials(
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    entry_point.run(args)
    xmlupload.assert_called_once_with(
        input_file=Path(DATA_XML_PATH),
        creds=creds,
        imgdir=".",
        config=UploadConfig(
            interrupt_after=None,
            skip_iiif_validation=False,
            skip_validation=False,
            skip_ontology_validation=False,
            ignore_duplicate_files_warning=False,
            validation_severity=ValidationSeverity.INFO,
            id2iri_replacement_file=None,
            do_not_request_resource_metadata_from_db=True,
        ),
    )


@patch("requests.get")
def test_check_api_health_success(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_get.return_value = mock_response

    # Should not raise any exception
    _check_api_health("http://0.0.0.0:3333")
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_not_healthy_local(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_not_healthy_server(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    expected_msg = regex.escape(
        "The DSP-API could not be reached (returned status 503). Please contact the DaSCH engineering team for help."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("https://api.dasch.swiss")
    mock_get.assert_called_once_with("https://api.dasch.swiss/health", timeout=2)


@patch("requests.get")
def test_check_api_health_connection_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")

    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_timeout(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")

    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


if __name__ == "__main__":
    pytest.main([__file__])
