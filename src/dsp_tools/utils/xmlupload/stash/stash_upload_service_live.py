from dataclasses import dataclass

from dsp_tools.models.connection import Connection
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.utils.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts


@dataclass
class StashUploadServiceLive:
    """Service that handles uploading of stashed links and standoff links to DSP."""

    con: Connection

    def upload_links(
        self,
        verbose: bool,
        id2iri_mapping: dict[str, str],
        stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
    ) -> dict[XMLResource, dict[XMLProperty, list[str]]]:
        """
        After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.

        Args:
            verbose: bool
            id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
            con: connection to DSP
            stashed_resptr_props: all resptr props that have been stashed

        Returns:
            nonapplied_resptr_props: the resptr props that could not be uploaded
        """
        return (
            upload_stashed_resptr_props(
                verbose=verbose, id2iri_mapping=id2iri_mapping, con=self.con, stashed_resptr_props=stashed_resptr_props
            )
            if stashed_resptr_props
            else {}
        )

    def upload_standoff_links(
        self,
        verbose: bool,
        id2iri_mapping: dict[str, str],
        stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    ) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
        """
        After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.

        Args:
            verbose: bool
            id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
            con: connection to DSP
            stashed_xml_texts: all xml texts that have been stashed

        Returns:
            nonapplied_xml_texts: the xml texts that could not be uploaded
        """
        return (
            upload_stashed_xml_texts(
                verbose=verbose, id2iri_mapping=id2iri_mapping, con=self.con, stashed_xml_texts=stashed_xml_texts
            )
            if stashed_xml_texts
            else {}
        )
