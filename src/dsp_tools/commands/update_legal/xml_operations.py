from pathlib import Path

import regex
from lxml import etree

from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.models import Authorships
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import UpdateCounter
from dsp_tools.xmllib.general_functions import find_license_in_string


def collect_metadata(
    res: etree._Element,
    properties: LegalProperties,
    defaults: LegalMetadataDefaults,
    counter: UpdateCounter,
    csv_metadata: LegalMetadata | None,
    treat_invalid_licenses_as_unknown: bool = False,
) -> LegalMetadata:
    """Collect legal metadata from CSV corrections, XML properties, or defaults."""
    license_val, copyright_val, authorships = _resolve_metadata_values(
        res=res,
        properties=properties,
        defaults=defaults,
        counter=counter,
        csv_metadata=csv_metadata,
        treat_invalid_licenses_as_unknown=treat_invalid_licenses_as_unknown,
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
    auth_text_to_id: dict[Authorships, int],
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
    counter: UpdateCounter,
    csv_metadata: LegalMetadata | None,
    treat_invalid_licenses_as_unknown: bool = False,
) -> tuple[str | None, str | None, Authorships]:
    """
    Resolve metadata values using priority: CSV > XML > defaults.

    Returns:
        Tuple of (license_val, copyright_val, authorships)
    """
    # Start with CSV corrections if available
    if csv_metadata:
        license_val = csv_metadata.license
        copyright_val = csv_metadata.copyright
        authorships = csv_metadata.authorships
    else:
        license_val = None
        copyright_val = None
        authorships = Authorships()

    # Collect license from XML, fall back to default
    if license_val is None and properties.license_prop:
        license_val = _extract_license_from_xml(
            res, properties.license_prop, counter, treat_invalid_licenses_as_unknown
        )
    if license_val is None and defaults.license_default:
        license_val = defaults.license_default.value

    # Collect copyright XML, fall back to default
    if copyright_val is None and properties.copyright_prop:
        copyright_val = _extract_copyright_from_xml(res, properties.copyright_prop)
    if copyright_val is None and defaults.copyright_default:
        copyright_val = defaults.copyright_default

    # Collect authorship from XML, fall back to default
    if authorships.is_empty() and properties.authorship_prop:
        authorships = _extract_authorships_from_xml(res, properties.authorship_prop)
    if authorships.is_empty() and defaults.authorship_default:
        authorships = Authorships.from_iterable({defaults.authorship_default})

    return license_val, copyright_val, authorships


def _extract_license_from_xml(
    res: etree._Element,
    license_prop: str,
    counter: UpdateCounter,
    treat_invalid_as_unknown: bool = False,
) -> str | None:
    """
    Extract license from XML property.

    - If one license is found and can be parsed, return its parsed value.
    - If the property is absent or empty, return None -> will fall back to default.
    - If multiple licenses are found, return a FIXME string.
    - If the license is invalid and treat_invalid_as_unknown is True, return 'unknown' and increment counter.
    - If the license is invalid and treat_invalid_as_unknown is False, return a FIXME string.

    Returns:
        License value, None, or FIXME string
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
        if treat_invalid_as_unknown:
            counter.invalid_licenses_replaced += 1
            return "http://rdfh.ch/licenses/unknown"
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


def _extract_authorships_from_xml(res: etree._Element, auth_prop: str) -> Authorships:
    auth_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{auth_prop}']/text")
    if not auth_elems:
        return Authorships()
    return Authorships.from_iterable([auth_elem.text.strip() for auth_elem in auth_elems if auth_elem.text])


def _apply_metadata_to_element(
    media_elem: etree._Element,
    license_val: str | None,
    copyright_val: str | None,
    authorships: Authorships,
    auth_text_to_id: dict[Authorships, int],
) -> None:
    """Apply legal metadata as attributes on the bitstream/iiif element."""
    if license_val and not is_fixme_value(license_val):
        media_elem.attrib["license"] = license_val
    if copyright_val and not is_fixme_value(copyright_val):
        media_elem.attrib["copyright-holder"] = copyright_val
    if not any(is_fixme_value(x) for x in authorships.elems):
        if (auth_id := auth_text_to_id.get(authorships)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[authorships] = auth_id
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


def add_authorship_definitions_to_xml(root: etree._Element, auth_text_to_id: dict[Authorships, int]) -> None:
    auth_defs = []
    for auth_text, auth_id in auth_text_to_id.items():
        auth_def = etree.Element("authorship", attrib={"id": f"authorship_{auth_id}"})
        for single_auth in auth_text.elems:
            auth_child = etree.Element("author")
            auth_child.text = single_auth
            auth_def.append(auth_child)
        auth_defs.append(auth_def)
    for auth_def in reversed(auth_defs):
        root.insert(0, auth_def)


def write_updated_xml(
    input_file: Path,
    root: etree._Element,
    counter: UpdateCounter,
    partial: bool = False,
) -> None:
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
    if counter.invalid_licenses_replaced > 0:
        print(f" - Invalid licenses replaced with 'unknown': {counter.invalid_licenses_replaced}\n")
