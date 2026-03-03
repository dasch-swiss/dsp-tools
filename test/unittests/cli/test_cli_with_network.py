from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.commands.start_stack.start_stack import StackConfiguration
from dsp_tools.commands.xmlupload.upload_config import UploadConfig

EXIT_CODE_TWO = 2

# ruff: noqa: ARG002 Unused function argument


PROJECT_JSON_PATH = Path("testdata/json-project/systematic-project-4123.json")
ID_2_IRI_JSON_PATH = "testdata/id2iri/test-id2iri-mapping.json"
DATA_XML_PATH = "testdata/xml-data/test-data-systematic-4123.xml"
MIGRATION_YAML_COMPLETE_PATH = "testdata/migration/migration-4125_complete.yaml"
MIGRATION_EXPORT_PATH = Path("testdata/migration/export-4125.zip")
MIGRATION_REFERENCE_PATH = Path("testdata/migration/migration-references-4125.json")


def test_invalid_arguments() -> None:
    args = "invalid".split()
    with pytest.raises(SystemExit) as ex:
        entry_point.run(args)
    assert ex.value.code == EXIT_CODE_TWO


class TestCreate:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_lists_section_from_project")
    def test_lists_validate(self, validate_lists_section_from_project: Mock, check_docker: Mock) -> None:
        validate_lists_section_from_project.return_value = (True, {})
        args = f"create --lists-only --validate-only {PROJECT_JSON_PATH}".split()
        entry_point.run(args)
        validate_lists_section_from_project.assert_called_once_with(PROJECT_JSON_PATH)

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.create_lists_only")
    def test_lists_create(self, create_lists: Mock, check_docker: Mock) -> None:
        create_lists.return_value = True
        args = f"create --lists-only {PROJECT_JSON_PATH}".split()
        creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        entry_point.run(args)
        create_lists.assert_called_once_with(
            project_file=PROJECT_JSON_PATH,
            creds=creds,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_project_only")
    def test_project_validate(self, validate_project_only: Mock, check_docker: Mock) -> None:
        validate_project_only.return_value = True
        args = f"create --validate-only {PROJECT_JSON_PATH}".split()
        entry_point.run(args)
        validate_project_only.assert_called_once_with(PROJECT_JSON_PATH, "http://0.0.0.0:3333")

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.create")
    def test_project_create(self, create: Mock, check_docker: Mock) -> None:
        args = f"create {PROJECT_JSON_PATH}".split()
        creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        entry_point.run(args)
        create.assert_called_once_with(
            project_file=PROJECT_JSON_PATH,
            creds=creds,
            exit_if_exists=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.create")
    def test_project_create_exit_if_exists(self, create: Mock, check_docker: Mock) -> None:
        args = f"create {PROJECT_JSON_PATH} --exit-if-exists".split()
        creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        entry_point.run(args)
        create.assert_called_once_with(
            project_file=PROJECT_JSON_PATH,
            creds=creds,
            exit_if_exists=True,
        )


class TestGet:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.get_project")
    def test_project_get(self, get_project: Mock, check_docker: Mock) -> None:
        project = "shortname"
        args = f"get --project {project} {PROJECT_JSON_PATH}".split()
        creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        entry_point.run(args)
        get_project.assert_called_once_with(
            project_identifier=project,
            outfile_path=str(PROJECT_JSON_PATH),
            creds=creds,
            verbose=False,
        )


class TestXmlupload:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_default(self, xmlupload: Mock, check_docker: Mock) -> None:
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
                id2iri_file=None,
                do_not_request_resource_metadata_from_db=False,
            ),
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.parse_and_validate_xml_file")
    def test_xmlupload_validate(self, validate_xml: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --validate-only {DATA_XML_PATH}".split()
        entry_point.run(args)
        validate_xml.assert_called_once_with(Path(DATA_XML_PATH))

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_no_iiif(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_skip_validation(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_ignore_duplicate_files_warning(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_default_validation_severity_warning(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_default_validation_severity_error(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_skip_ontology_validation(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_interrupt_after(self, xmlupload: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_id2iri_file(self, xmlupload: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --id2iri-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
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
            config=UploadConfig(id2iri_file=ID_2_IRI_JSON_PATH),
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    def test_xmlupload_do_not_request_resource_metadata_from_db(self, xmlupload: Mock, check_docker: Mock) -> None:
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
                id2iri_file=None,
                do_not_request_resource_metadata_from_db=True,
            ),
        )


class TestValidateData:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_default(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_ignore_duplicate_files(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_save_graph(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_other_server(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_other_creds(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_skip_ontology_validation(self, validate_data: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_id2iri_file(self, validate_data: Mock, check_docker: Mock) -> None:
        args = f"validate-data --id2iri-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
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
            id2iri_file=ID_2_IRI_JSON_PATH,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.validate_data")
    def test_validate_data_do_not_request_resource_metadata_from_db(
        self, validate_data: Mock, check_docker: Mock
    ) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=True,
        )


class TestResumeXmlupload:
    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.resume_xmlupload")
    def test_resume_xmlupload_default(self, resume_xmlupload: Mock, check_input_dependencies: Mock) -> None:
        args = "resume-xmlupload".split()
        creds = ServerCredentials(
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            dsp_ingest_url="http://0.0.0.0:3340",
        )
        entry_point.run(args)
        resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=False)

    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.resume_xmlupload")
    def test_resume_xmlupload_skip_first_resource(self, resume_xmlupload: Mock, check_input_dependencies: Mock) -> None:
        args = "resume-xmlupload --skip-first-resource".split()
        creds = ServerCredentials(
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            dsp_ingest_url="http://0.0.0.0:3340",
        )
        entry_point.run(args)
        resume_xmlupload.assert_called_once_with(creds=creds, skip_first_resource=True)


class TestIngestUploads:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.upload_files")
    def test_upload_files_localhost(self, upload_files: Mock, check_docker: Mock) -> None:
        args = f"upload-files {DATA_XML_PATH}".split()
        entry_point.run(args)
        creds = ServerCredentials(
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            dsp_ingest_url="http://0.0.0.0:3340",
        )
        upload_files.assert_called_once_with(xml_file=Path(DATA_XML_PATH), creds=creds, imgdir=Path("."))

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.upload_files")
    def test_upload_files_remote(self, upload_files: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.ingest_files")
    def test_ingest_files_localhost(self, ingest_files: Mock, check_input_dependencies: Mock) -> None:
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

    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.ingest_files")
    def test_ingest_files_remote(self, ingest_files: Mock, check_input_dependencies: Mock) -> None:
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

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_localhost(self, ingest_xmlupload: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_skip_validation(self, ingest_xmlupload: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_interrupt_after(self, ingest_xmlupload: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_remote(self, ingest_xmlupload: Mock, check_docker: Mock) -> None:
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_id2iri_file(self, ingest_xmlupload: Mock, check_docker: Mock) -> None:
        args = f"ingest-xmlupload --id2iri-file {ID_2_IRI_JSON_PATH} {DATA_XML_PATH}".split()
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
            id2iri_file=ID_2_IRI_JSON_PATH,
            do_not_request_resource_metadata_from_db=False,
        )

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.ingest_xmlupload")
    def test_ingest_xmlupload_do_not_request_resource_metadata_from_db(
        self, ingest_xmlupload: Mock, check_docker: Mock
    ) -> None:
        args = f"ingest-xmlupload {DATA_XML_PATH} --do-not-request-resource-metadata-from-db".split()
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
            id2iri_file=None,
            do_not_request_resource_metadata_from_db=True,
        )


class TestStartStack:
    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_default(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_max_file_size(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_prune(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_no_prune(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_latest(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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

    @patch("dsp_tools.cli.utils.check_docker_health")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.start_stack")
    @patch("dsp_tools.commands.start_stack.start_stack.StackHandler.__init__", return_value=None)
    def test_start_stack_with_test_data(self, mock_init: Mock, start_stack: Mock, check_docker: Mock) -> None:
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


@patch("dsp_tools.commands.start_stack.start_stack.StackHandler.stop_stack")
def test_stop_stack(stop_stack: Mock) -> None:
    args = "stop-stack".split()
    entry_point.run(args)
    stop_stack.assert_called_once_with()


class TestUpdatePromptFlag:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    @patch("dsp_tools.cli.entry_point._check_version")
    def test_suppress_update_prompt_flag_absent(self, check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --user=testuser {DATA_XML_PATH}".split()
        entry_point.run(args)
        check_version.assert_called_once()
        xmlupload.assert_called_once()

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    @patch("dsp_tools.cli.entry_point._check_version")
    def test_suppress_update_prompt_leftmost(self, check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --suppress-update-prompt --user=testuser {DATA_XML_PATH}".split()
        entry_point.run(args)
        check_version.assert_not_called()
        xmlupload.assert_called_once()

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    @patch("dsp_tools.cli.entry_point._check_version")
    def test_suppress_update_prompt_middle(self, check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --user=testuser --suppress-update-prompt {DATA_XML_PATH}".split()
        entry_point.run(args)
        check_version.assert_not_called()
        xmlupload.assert_called_once()

    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.xmlupload")
    @patch("dsp_tools.cli.entry_point._check_version")
    def test_suppress_update_prompt_rightmost(self, check_version: Mock, xmlupload: Mock, check_docker: Mock) -> None:
        args = f"xmlupload --user=testuser {DATA_XML_PATH} --suppress-update-prompt".split()
        entry_point.run(args)
        check_version.assert_not_called()
        xmlupload.assert_called_once()


class TestMigrationExport:
    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.export")
    def test_migration_export(self, mock_export: Mock, check_input_deps: Mock) -> None:
        mock_export.return_value = True, None
        source = ServerInfo(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        config = MigrationConfig(
            shortcode="4125",
            export_savepath=MIGRATION_EXPORT_PATH,
            reference_savepath=MIGRATION_REFERENCE_PATH,
            keep_local_export=False,
        )
        args = f"migration export {MIGRATION_YAML_COMPLETE_PATH}".split()
        entry_point.run(args)
        mock_export.assert_called_once_with(source, config)

    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.export")
    def test_migration_export_keep_export(self, mock_export: Mock, check_input_deps: Mock) -> None:
        mock_export.return_value = True, None
        source = ServerInfo(server="http://0.0.0.0:3333", user="root1@example.com", password="test1")
        config = MigrationConfig(
            shortcode="4125",
            export_savepath=MIGRATION_EXPORT_PATH,
            reference_savepath=MIGRATION_REFERENCE_PATH,
            keep_local_export=True,
        )
        args = "migration export testdata/migration/migration-4125_complete_keep_export.yaml".split()
        entry_point.run(args)
        mock_export.assert_called_once_with(source, config)

    def test_migration_export_source_server_missing(self) -> None:
        args = "migration export testdata/migration/migration-4125_target_only.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)

    def test_migration_export_config_file_not_found(self) -> None:
        args = "migration export nonexistent-config.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)


class TestMigrationDownload:
    @patch("dsp_tools.cli.utils._check_network_health")
    @patch("dsp_tools.cli.call_action_with_network.download")
    def test_migration_download(self, mock_download: Mock, check_network: Mock) -> None:
        mock_download.return_value = True, None
        source = ServerInfo(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        config = MigrationConfig(
            shortcode="4125",
            export_savepath=MIGRATION_EXPORT_PATH,
            reference_savepath=MIGRATION_REFERENCE_PATH,
            keep_local_export=False,
        )
        args = f"migration download {MIGRATION_YAML_COMPLETE_PATH}".split()
        entry_point.run(args)
        mock_download.assert_called_once_with(source, config)

    def test_migration_download_source_server_missing(self) -> None:
        args = "migration download testdata/migration/migration-4125_target_only.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)

    def test_migration_download_config_file_not_found(self) -> None:
        args = "migration download nonexistent-config.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)


class TestMigrationImport:
    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.import_zip")
    def test_migration_import(self, mock_import_zip: Mock, check_input_deps: Mock) -> None:
        mock_import_zip.return_value = True
        target = ServerInfo(server="https://api.some-project.dasch.swiss", user="root@example.com", password="test")
        config = MigrationConfig(
            shortcode="4125",
            export_savepath=MIGRATION_EXPORT_PATH,
            reference_savepath=MIGRATION_REFERENCE_PATH,
            keep_local_export=False,
        )
        args = "migration import testdata/migration/migration-4125_complete.yaml".split()
        entry_point.run(args)
        mock_import_zip.assert_called_once_with(target, config)

    def test_migration_import_target_server_missing(self) -> None:
        args = "migration import testdata/migration/migration-4125_source_only.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)

    def test_migration_import_config_file_not_found(self) -> None:
        args = "migration import nonexistent-config.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)


class TestMigrationCleanUp:
    @patch("dsp_tools.cli.call_action_with_network.check_input_dependencies")
    @patch("dsp_tools.cli.call_action_with_network.clean_up")
    def test_migration_import(self, clean_up: Mock, check_input_deps: Mock) -> None:
        clean_up.return_value = True
        source = ServerInfo(server="http://0.0.0.0:3333", user="root@example.com", password="test")
        target = ServerInfo(server="https://api.some-project.dasch.swiss", user="root@example.com", password="test")
        config = MigrationConfig(
            shortcode="4125",
            export_savepath=MIGRATION_EXPORT_PATH,
            reference_savepath=MIGRATION_REFERENCE_PATH,
            keep_local_export=False,
        )
        info = MigrationInfo(config, source, target)
        args = f"migration clean-up {MIGRATION_YAML_COMPLETE_PATH}".split()
        entry_point.run(args)
        clean_up.assert_called_once_with(info)

    def test_migration_import_config_file_not_found(self) -> None:
        args = "migration clean-up nonexistent-config.yaml".split()
        with pytest.raises(SystemExit):
            entry_point.run(args)


if __name__ == "__main__":
    pytest.main([__file__])
