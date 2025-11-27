from pathlib import Path

from lxml import etree

from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.csv_operations import read_corrections_csv
from dsp_tools.commands.update_legal.csv_operations import write_problems_to_csv
from dsp_tools.commands.update_legal.models import Authorships
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import Problem
from dsp_tools.commands.update_legal.models import UpdateCounter
from dsp_tools.commands.update_legal.xml_operations import add_authorship_definitions_to_xml
from dsp_tools.commands.update_legal.xml_operations import apply_metadata_to_resource
from dsp_tools.commands.update_legal.xml_operations import collect_metadata
from dsp_tools.commands.update_legal.xml_operations import write_updated_xml
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import transform_into_localnames


def update_legal_metadata(
    input_file: Path,
    properties: LegalProperties,
    defaults: LegalMetadataDefaults,
    fixed_errors_file: Path | None = None,
    treat_invalid_licenses_as_unknown: bool = False,
) -> bool:
    """
    Update legal metadata in an XML file, converting text properties to bitstream attributes.

    Args:
        input_file: Path to the input XML file
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        fixed_errors_file: Path to CSV file with corrected values
        treat_invalid_licenses_as_unknown: If True, invalid licenses are replaced with 'unknown'

    Returns:
        True if all legal metadata could be updated, False if CSV error file was created
    """
    csv_corrections = None
    if fixed_errors_file:
        csv_corrections = read_corrections_csv(fixed_errors_file)

    root = parse_xml_file(input_file)
    root = transform_into_localnames(root)
    _validate_flags(root, properties)

    root_updated, counter, problems = _update_xml_tree(
        root=root,
        properties=properties,
        defaults=defaults,
        csv_corrections=csv_corrections,
        treat_invalid_licenses_as_unknown=treat_invalid_licenses_as_unknown,
    )

    if len(problems) == 0:
        # Success - write fully updated XML with _updated suffix
        write_updated_xml(input_file, root_updated, counter, partial=False)
        return True
    else:
        # Partial update - write both CSV and partial XML
        write_problems_to_csv(input_file, problems)
        write_updated_xml(input_file, root_updated, counter, partial=True)
        return False


def _validate_flags(root: etree._Element, properties: LegalProperties) -> None:
    if not properties.has_any_property():
        raise InputError("At least one property (authorship_prop, copyright_prop, license_prop) must be provided")
    text_prop_names = {x for x in root.xpath("//text-prop/@name")}
    inexisting_props = [
        x
        for x in [properties.authorship_prop, properties.copyright_prop, properties.license_prop]
        if x and x not in text_prop_names
    ]
    if inexisting_props:
        raise InputError(f"The following properties do not exist in the XML file: {', '.join(inexisting_props)}")


def _update_xml_tree(
    root: etree._Element,
    properties: LegalProperties,
    defaults: LegalMetadataDefaults,
    csv_corrections: dict[str, LegalMetadata] | None = None,
    treat_invalid_licenses_as_unknown: bool = False,
) -> tuple[etree._Element, UpdateCounter, list[Problem]]:
    """
    Update the XML tree with legal metadata, applying corrections and defaults.
    Resources without problems are fully updated (metadata applied, text properties removed).
    Resources with problems are left unchanged in the XML, but problems are collected for CSV output.

    Args:
        root: The XML root element
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        csv_corrections: Dictionary of corrections from CSV (or None)
        treat_invalid_licenses_as_unknown: If True, invalid licenses are replaced with 'unknown'

    Returns:
        Tuple of (updated root element, counter of updated resources, list of problems)
    """
    auth_text_to_id: dict[Authorships, int] = {}
    problems: list[Problem] = []
    counter = UpdateCounter()

    for res in root.iterchildren(tag="resource"):
        if not (media_tag_candidates := res.xpath("bitstream|iiif-uri")):
            continue

        res_id = res.attrib["id"]
        media_elem = media_tag_candidates[0]
        csv_metadata = csv_corrections.get(res_id) if csv_corrections else None

        metadata = collect_metadata(
            res=res,
            properties=properties,
            defaults=defaults,
            counter=counter,
            csv_metadata=csv_metadata,
            treat_invalid_licenses_as_unknown=treat_invalid_licenses_as_unknown,
        )

        if _has_problems(metadata):
            authorships = sorted(x for x in metadata.authorships.elems if x) or ["FIXME: Authorship missing"]
            problem = Problem(
                file_or_iiif_uri=str(media_elem.text).strip(),
                res_id=res_id,
                license=metadata.license or "FIXME: License missing",
                copyright=metadata.copyright or "FIXME: Copyright missing",
                authorships=authorships,
            )
            problems.append(problem)
        elif metadata.any():
            apply_metadata_to_resource(
                res=res,
                media_elem=media_elem,
                metadata=metadata,
                properties=properties,
                auth_text_to_id=auth_text_to_id,
            )
            _update_counter(counter, metadata)

    if auth_text_to_id:
        add_authorship_definitions_to_xml(root, auth_text_to_id)

    return root, counter, problems


def _has_problems(metadata: LegalMetadata) -> bool:
    """
    Check if metadata has any missing or invalid fields that should be reported in CSV.

    Args:
        metadata: The legal metadata to check

    Returns:
        True if there are problems, False otherwise
    """
    has_license_problem = metadata.license is None or is_fixme_value(metadata.license)
    has_copyright_problem = metadata.copyright is None or is_fixme_value(metadata.copyright)

    if not any(x for x in metadata.authorships.elems if x):
        has_authorship_problem = True
    elif any(is_fixme_value(x) for x in metadata.authorships.elems):
        has_authorship_problem = True
    else:
        has_authorship_problem = False

    return has_license_problem or has_copyright_problem or has_authorship_problem


def _update_counter(counter: UpdateCounter, metadata: LegalMetadata) -> None:
    counter.resources_updated += 1
    if metadata.license:
        counter.licenses_set += 1
    if metadata.copyright:
        counter.copyrights_set += 1
    if metadata.authorships:
        counter.authorships_set += 1
