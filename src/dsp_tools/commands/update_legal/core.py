from pathlib import Path

from lxml import etree

from dsp_tools.commands.update_legal.csv_operations import ProblemAggregator
from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.csv_operations import read_corrections_csv
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import MetadataDefaults
from dsp_tools.commands.update_legal.models import Problem
from dsp_tools.commands.update_legal.xml_operations import add_authorship_definitions
from dsp_tools.commands.update_legal.xml_operations import update_one_xml_resource
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _transform_into_localnames


def update_legal_metadata(
    input_file: Path,
    properties: LegalProperties,
    defaults: MetadataDefaults,
    fixed_errors_file: Path | None = None,
) -> bool:
    """
    Update legal metadata in an XML file, converting text properties to bitstream attributes.

    Args:
        input_file: Path to the input XML file
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        fixed_errors_file: Path to CSV file with corrected values

    Returns:
        True if XML was successfully written, False if CSV error file was created
    """
    csv_corrections = None
    if fixed_errors_file:
        csv_corrections = read_corrections_csv(fixed_errors_file)

    root = _parse_xml_file(input_file)
    root = _transform_into_localnames(root)

    root_updated, problems = _update_xml_tree(
        root=root,
        properties=properties,
        defaults=defaults,
        csv_corrections=csv_corrections,
    )

    if problems:
        aggregator = ProblemAggregator(problems)
        csv_path = aggregator.save_to_csv(input_file)
        print(f"\n⚠️  Legal metadata contains errors. Please fix them in the CSV file:\n    {csv_path}")
        print(f"\nAfter fixing the errors, rerun the command with:\n    --fixed_errors={csv_path}")
        return False

    # No problems - write the updated XML
    root_new = etree.ElementTree(root_updated)
    output_file = input_file.with_stem(f"{input_file.stem}_updated")
    etree.indent(root_new, space="    ")
    root_new.write(output_file, pretty_print=True, encoding="utf-8", doctype='<?xml version="1.0" encoding="UTF-8"?>')

    print(f"\n✓ Successfully updated legal metadata. Output written to:\n    {output_file}")
    return True


def _update_xml_tree(
    root: etree._Element,
    properties: LegalProperties,
    defaults: MetadataDefaults,
    csv_corrections: dict[str, LegalMetadata] | None = None,
) -> tuple[etree._Element, list[Problem]]:
    """
    Update the XML tree with legal metadata, applying corrections and defaults.

    Args:
        root: The XML root element
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        csv_corrections: Dictionary of corrections from CSV (or None)

    Returns:
        Tuple of (updated root element, list of problems)
    """
    if not properties.has_any_property():
        raise InputError("At least one property (authorship_prop, copyright_prop, license_prop) must be provided")

    auth_text_to_id: dict[str, int] = {}
    problems: list[Problem] = []

    # Process each resource with multimedia
    for res in root.iterchildren(tag="resource"):
        if not (media_tag_candidates := res.xpath("bitstream|iiif-uri")):
            continue

        res_id = res.attrib["id"]
        media_elem = media_tag_candidates[0]
        csv_metadata = csv_corrections.get(res_id) if csv_corrections else None

        metadata = update_one_xml_resource(
            res=res,
            media_elem=media_elem,
            properties=properties,
            defaults=defaults,
            csv_metadata=csv_metadata,
            auth_text_to_id=auth_text_to_id,
        )

        if has_problems(metadata):
            problem = Problem(
                file_or_iiif_uri=str(media_elem.text).strip(),
                res_id=res_id,
                license=metadata.license or "FIXME: License missing",
                copyright=metadata.copyright or "FIXME: Copyright missing",
                authorships=metadata.authorships if metadata.authorships else ["FIXME: Authorship missing"],
            )
            problems.append(problem)

    if auth_text_to_id:
        add_authorship_definitions(root, auth_text_to_id)

    return root, problems


def has_problems(metadata: LegalMetadata) -> bool:
    """
    Check if metadata has any missing or invalid fields that should be reported in CSV.

    Args:
        metadata: The legal metadata to check

    Returns:
        True if there are problems, False otherwise
    """
    has_license_problem = metadata.license is None or is_fixme_value(metadata.license)
    has_copyright_problem = metadata.copyright is None or is_fixme_value(metadata.copyright)

    if not metadata.authorships:
        has_authorship_problem = True
    elif any(is_fixme_value(x) for x in metadata.authorships):
        has_authorship_problem = True
    else:
        has_authorship_problem = False

    return has_license_problem or has_copyright_problem or has_authorship_problem
