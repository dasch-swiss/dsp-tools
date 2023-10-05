from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.xmlupload.stash.stash_upload_service import StashUploadService


def upload_stashed_links(
    stashUploadService: StashUploadService,
    verbose: bool,
    id2iri_mapping: dict[str, str],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
) -> tuple[
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]],
]:
    """Uploads all stashed links and standoff links to DSP.

    Args:
        stashUploadService: service that handles uploading of stashed links and standoff links to DSP
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        stashed_xml_texts: all xml text props that have been stashed
        stashed_resptr_props: all resptr props that have been stashed

    Returns:
        tuple[
            dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
            dict[XMLResource, dict[XMLProperty, list[str]]],
        ]: resptr and standoff link stashes that could not be uploaded
    """
    nonapplied_links = stashUploadService.upload_links(
        verbose=verbose,
        id2iri_mapping=id2iri_mapping,
        stashed_resptr_props=stashed_resptr_props,
    )
    nonapplied_standoff_links = stashUploadService.upload_standoff_links(
        verbose=verbose,
        id2iri_mapping=id2iri_mapping,
        stashed_xml_texts=stashed_xml_texts,
    )
    return nonapplied_standoff_links, nonapplied_links
