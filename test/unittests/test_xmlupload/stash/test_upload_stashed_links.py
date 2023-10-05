from typing import TypeAlias

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.xmlupload.stash.upload_stashed_links import upload_stashed_links

ResptrStash: TypeAlias = dict[XMLResource, dict[XMLProperty, list[str]]]
StandoffStash: TypeAlias = dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]


class StashUploadServiceMock:
    """Service that handles uploading of stashed links and standoff links to DSP."""

    def upload_links(  # pylint: disable=missing-function-docstring
        self,
        verbose: bool,  # pylint: disable=unused-argument
        id2iri_mapping: dict[str, str],  # pylint: disable=unused-argument
        stashed_resptr_props: ResptrStash,  # pylint: disable=unused-argument
    ) -> dict[XMLResource, dict[XMLProperty, list[str]]]:  # pylint: disable=unused-argument
        return {}

    def upload_standoff_links(  # pylint: disable=missing-function-docstring
        self,
        verbose: bool,  # pylint: disable=unused-argument
        id2iri_mapping: dict[str, str],  # pylint: disable=unused-argument
        stashed_xml_texts: StandoffStash,  # pylint: disable=unused-argument
    ) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
        return {}


class TestUploadStashedLinks:
    """Class for testing the upload_stashed_links function."""

    def test_upload_stashed_links_no_stashed_links(self) -> None:
        """Test that upload_stashed_links returns empty dicts if no stashed links are given."""
        serviceMock = StashUploadServiceMock()
        result = upload_stashed_links(
            stashUploadService=serviceMock,
            verbose=False,
            id2iri_mapping={},
            stashed_xml_texts={},
            stashed_resptr_props={},
        )
        assert result == ({}, {})
