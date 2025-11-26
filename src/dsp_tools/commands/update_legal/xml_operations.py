from pathlib import Path

import regex
from lxml import etree

from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import UpdateCounter
from dsp_tools.xmllib.general_functions import find_license_in_string


def collect_metadata(
    res: etree._Element,
    properties: LegalProperties,
    defaults: LegalMetadataDefaults,
    csv_metadata: LegalMetadata | None,
) -> LegalMetadata:
    """
    Collect legal metadata from CSV corrections, XML properties, or defaults.

    Args:
        res: The resource element to extract metadata from
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        csv_metadata: Corrections from CSV file

    Returns:
        LegalMetadata with collected values
    """
    license_val, copyright_val, authorships = _resolve_metadata_values(
        res=res,
        properties=properties,
        defaults=defaults,
        csv_metadata=csv_metadata,
    )
    return LegalMetadata(
        license=license_val,
        copyright=copyright_val,
        authorships=authorships,
    )


def apply_metadata_to_resource(
    res: etree._Element,
    media_elem: etree._Element,
    metadata: LegalMetadata,
    properties: LegalProperties,
    auth_text_to_id: dict[str, int],
) -> None:
    """
    Apply legal metadata to a resource's media element and remove old text properties.
    This function modifies the XML tree in-place.

    Args:
        res: The resource element
        media_elem: The bitstream or iiif-uri element to apply attributes to
        metadata: The legal metadata to apply
        properties: Configuration for property names (used for removal)
        auth_text_to_id: Dictionary to track unique authorships (modified in-place)
    """
    _apply_metadata_to_element(
        media_elem=media_elem,
        license_val=metadata.license,
        copyright_val=metadata.copyright,
        authorships=metadata.authorships,
        auth_text_to_id=auth_text_to_id,
    )
    _remove_text_properties(res, properties)


def _resolve_metadata_values(
    res: etree._Element,
    properties: LegalProperties,
    defaults: LegalMetadataDefaults,
    csv_metadata: LegalMetadata | None,
) -> tuple[str | None, str | None, list[str]]:
    """
    Resolve metadata values using priority: CSV > XML > defaults.

    Returns:
        Tuple of (license_val, copyright_val, authorships)
    """
    # Start with CSV corrections if available
    if csv_metadata:
        license_val = csv_metadata.license
        copyright_val = csv_metadata.copyright
        authorships = csv_metadata.authorships.copy()
    else:
        license_val = None
        copyright_val = None
        authorships = []

    # Collect license from XML, fall back to default
    if license_val is None and properties.license_prop:
        license_val = _extract_license_from_xml(res, properties.license_prop)
    if license_val is None and defaults.license_default:
        license_val = defaults.license_default.value

    # Collect copyright XML, fall back to default
    if copyright_val is None and properties.copyright_prop:
        copyright_val = _extract_copyright_from_xml(res, properties.copyright_prop)
    if copyright_val is None and defaults.copyright_default:
        copyright_val = defaults.copyright_default

    # Collect authorship from XML, fall back to default
    if not authorships and properties.authorship_prop:
        authorships = _extract_authorships_from_xml(res, properties.authorship_prop)
    if not authorships and defaults.authorship_default:
        authorships = [defaults.authorship_default]

    return license_val, copyright_val, authorships


def _extract_license_from_xml(res: etree._Element, license_prop: str) -> str | None:
    """
    Extract license from XML property.

    - If one license is found and can be parsed, return its parsed value.
    - If the property is absent or empty, return None -> will fall back to default.
    - If multiple licenses are found, or if the license is invalid, return a FIXME string.
    """
    license_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{license_prop}']/text")
    if not license_elems:
        return None
    if len(license_elems) > 1:
        license_texts = [elem.text.strip() for elem in license_elems if elem.text and elem.text.strip()]
        return f"FIXME: Multiple licenses found. Choose one: {', '.join(license_texts)}"
    license_elem = license_elems[0]
    if not license_elem.text or not (license_text := license_elem.text.strip()):
        return None
    if not (lic := find_license_in_string(license_text)):
        return f"FIXME: Invalid license: {license_text}"
    return lic.value


def _extract_copyright_from_xml(res: etree._Element, copy_prop: str) -> str | None:
    copy_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{copy_prop}']/text")
    if not copy_elems:
        return None
    if len(copy_elems) > 1:
        copy_texts = [elem.text.strip() for elem in copy_elems if elem.text and elem.text.strip()]
        return f"FIXME: Multiple copyrights found. Choose one: {', '.join(copy_texts)}"
    copy_elem = copy_elems[0]
    if not copy_elem.text or not (copy_text := copy_elem.text.strip()):
        return None
    return copy_text


def _extract_authorships_from_xml(res: etree._Element, auth_prop: str) -> list[str]:
    auth_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{auth_prop}']/text")
    if not auth_elems:
        return []
    authorships = []
    for auth_elem in auth_elems:
        if auth_elem.text and (auth_text := auth_elem.text.strip()):
            authorships.append(auth_text)
    return authorships


def _apply_metadata_to_element(
    media_elem: etree._Element,
    license_val: str | None,
    copyright_val: str | None,
    authorships: list[str],
    auth_text_to_id: dict[str, int],
) -> None:
    """Apply legal metadata as attributes on the bitstream/iiif element."""
    if license_val and not is_fixme_value(license_val):
        media_elem.attrib["license"] = license_val
    if copyright_val and not is_fixme_value(copyright_val):
        media_elem.attrib["copyright-holder"] = copyright_val
    if authorships and not any(is_fixme_value(x) for x in authorships):
        auth_text = ", ".join([x.strip() for x in authorships])
        if (auth_id := auth_text_to_id.get(auth_text)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[auth_text] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"


def _remove_text_properties(res: etree._Element, properties: LegalProperties) -> None:
    """Remove the text properties from XML (they're now attributes on media element)."""
    if properties.authorship_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.authorship_prop}']"):
            res.remove(prop_elem)
    if properties.copyright_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.copyright_prop}']"):
            res.remove(prop_elem)
    if properties.license_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.license_prop}']"):
            res.remove(prop_elem)


def add_authorship_definitions_to_xml(root: etree._Element, auth_text_to_id: dict[str, int]) -> None:
    auth_defs = []
    for auth_text, auth_id in auth_text_to_id.items():
        auth_def = etree.Element("authorship", attrib={"id": f"authorship_{auth_id}"})
        for single_auth in auth_text.split(", "):
            auth_child = etree.Element("author")
            auth_child.text = single_auth.strip()
            auth_def.append(auth_child)
        auth_defs.append(auth_def)
    for auth_def in reversed(auth_defs):
        root.insert(0, auth_def)


def write_final_xml(
    input_file: Path,
    root: etree._Element,
    counter: UpdateCounter,
    partial: bool = False,
) -> bool:
    """
    Write the updated XML to an output file.

    Args:
        input_file: Path to the input XML file
        root: The updated XML root element
        counter: Counter tracking number of updates
        partial: If True, this is a partial update with some resources still having errors

    Returns:
        True indicating successful write
    """
    root_new = etree.ElementTree(root)

    base_filename = regex.sub(r"(_PARTIALLY_updated|_updated)$", "", input_file.stem)
    if partial and input_file.stem.endswith("_PARTIALLY_updated"):
        # Overwrite the existing partial file
        output_file = input_file
    elif partial:
        # Create new partial file
        output_file = input_file.with_stem(f"{base_filename}_PARTIALLY_updated")
    else:
        # Success - create final updated file
        output_file = input_file.with_stem(f"{base_filename}_updated")

    etree.indent(root_new, space="    ")
    root_new.write(output_file, pretty_print=True, encoding="utf-8", doctype='<?xml version="1.0" encoding="UTF-8"?>')

    if partial:
        print(f"\n⚠️  Partial update completed. Output written to: {output_file}")
        print("   Some resources still have errors - check the CSV error file.\n")
    else:
        print(f"\n✓ Successfully updated all legal metadata. Output written to: {output_file}\n")

    print(f" - Resources updated: {counter.resources_updated}\n")
    print(f" - Licenses set: {counter.licenses_set}\n")
    print(f" - Copyrights set: {counter.copyrights_set}\n")
    print(f" - Authorships set: {counter.authorships_set}\n")
    return True
