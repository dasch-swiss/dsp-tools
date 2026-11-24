from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import _validation_should_be_skipped
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.commands.xmlupload.upload_config import UploadConfig

MODULE = "dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml"
LOCAL_SERVER = "http://0.0.0.0:3333"
PROMPT_TARGET = f"{MODULE}.prompt_until_valid_answer"


class TestValidationShouldBeSkipped:
    def test_not_requested(self) -> None:
        with patch(PROMPT_TARGET, side_effect=AssertionError("must not prompt")):
            assert not _validation_should_be_skipped(UploadConfig(skip_validation=False), True)

    def test_requested_local(self) -> None:
        with patch(PROMPT_TARGET, side_effect=AssertionError("must not prompt")):
            assert _validation_should_be_skipped(UploadConfig(skip_validation=True), False)

    @pytest.mark.parametrize(("answer", "expected"), [("yes", True), ("no", False)])
    def test_requested_prod_like_prompts(self, answer: str, expected: bool) -> None:
        with patch(PROMPT_TARGET, return_value=answer) as prompt:
            assert _validation_should_be_skipped(UploadConfig(skip_validation=True), True) is expected
        prompt.assert_called_once()


def test_default_authorship_reaches_processed_resources() -> None:
    root = Mock()
    root.attrib = {"shortcode": "0001"}
    project_client = Mock()
    project_client.get_project_iri.return_value = "http://rdfh.ch/projects/0001"
    project_client.get_project_shortname.return_value = "my-proj"
    creds = ServerCredentials(user="root@example.com", password="test", server=LOCAL_SERVER)
    config_server_info = UploadConfig(skip_validation=True).with_server_info(server=LOCAL_SERVER, shortcode="0001")
    with (
        patch(f"{MODULE}.parse_and_clean_xml_file", return_value=root),
        patch(f"{MODULE}._replace_filepaths_with_internal_filename_from_ingest", return_value=root),
        patch(f"{MODULE}.AuthenticationClientLive"),
        patch(f"{MODULE}.ProjectClientLive", return_value=project_client),
        patch(f"{MODULE}.check_on_behalf_of_user_for_data_import") as check_user,
        patch(f"{MODULE}.resolve_project_default_authorship", return_value=["Daisy Duck"]),
        patch.object(UploadConfig, "with_server_info", return_value=config_server_info),
        patch(f"{MODULE}.ListGetClientLive"),
        patch(f"{MODULE}.LegalInfoClientLive"),
        patch(f"{MODULE}.get_parsed_resources_and_mappers", return_value=([], Mock())),
        patch(f"{MODULE}.validate_iiif_uris"),
        patch(f"{MODULE}.get_processed_resources", return_value=[]) as get_processed,
        patch(f"{MODULE}.upload_copyright_holders"),
        patch(f"{MODULE}.make_payload_files", return_value=Mock()),
        patch(f"{MODULE}.write_minted_mapping"),
        patch(f"{MODULE}.write_payload_file"),
        patch(f"{MODULE}.DataImportClientLive"),
        patch(f"{MODULE}.run_import", return_value=True),
    ):
        result = ingest_xmlupload(
            Path("data.xml"),
            creds,
            on_behalf_of_user="my-proj@admin.dasch.swiss",
            skip_validation=True,
        )
    assert result
    check_user.assert_called_once_with("my-proj@admin.dasch.swiss", "my-proj", LOCAL_SERVER)
    assert get_processed.call_args[0][3] == ["Daisy Duck"]
