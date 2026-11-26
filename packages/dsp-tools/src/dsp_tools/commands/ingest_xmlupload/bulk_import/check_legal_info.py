from dsp_tools.commands.ingest_xmlupload.exceptions import LegalInfoMissingError
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def check_legal_info_is_complete(resources: list[ParsedResource]) -> None:
    """
    Stops the bulk data import before anything is written to the server if a file has no legal info.
    On test servers, DSP-TOOLS fills in missing legal info with placeholders,
    but the bulk data import of DSP-API rejects them (DEV-8079).

    Raises:
        LegalInfoMissingError: if a file has no license, copyright holder or authorship
    """
    res_ids = [res.res_id for res in resources if res.file_value and not _is_complete(res.file_value.metadata)]
    if res_ids:
        raise LegalInfoMissingError(res_ids)


def _is_complete(metadata: ParsedFileValueMetadata) -> bool:
    return bool(metadata.license_iri and metadata.copyright_holder and metadata.authorship_id)
