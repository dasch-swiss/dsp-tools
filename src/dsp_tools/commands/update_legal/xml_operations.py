from lxml import etree

from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import MetadataDefaults
from dsp_tools.xmllib.general_functions import find_license_in_string


def extract_license_from_xml(res: etree._Element, license_prop: str) -> str | None:
    """Extract license from XML property."""
    license_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{license_prop}']/text")
    if not license_elems:
        return None
    # Use first element if multiple exist
    license_elem = license_elems[0]
    if not license_elem.text or not (license_text := license_elem.text.strip()):
        return None
    # Try to parse the license
    if not (lic := find_license_in_string(license_text)):
        # Unknown license - mark as FIXME
        return f"FIXME: Invalid license: {license_text}"
    return lic.value


def apply_license_default(license_default: str) -> str | None:
    """Apply default license value, parsing it if possible."""
    if not (lic := find_license_in_string(license_default)):
        # Unknown license - mark as FIXME
        return f"FIXME: Invalid license: {license_default}"
    return lic.value


def extract_copyright_from_xml(res: etree._Element, copy_prop: str) -> str | None:
    """Extract copyright from XML property."""
    copy_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{copy_prop}']/text")
    if not copy_elems:
        return None
    # Use first element if multiple exist
    copy_elem = copy_elems[0]
    if not copy_elem.text or not (copy_text := copy_elem.text.strip()):
        return None
    return copy_text


def extract_authorships_from_xml(res: etree._Element, auth_prop: str) -> list[str]:
    """Extract authorships from XML property."""
    auth_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{auth_prop}']/text")
    if not auth_elems:
        return []

    authorships = []
    for auth_elem in auth_elems:
        if auth_elem.text and (auth_text := auth_elem.text.strip()):
            authorships.append(auth_text)

    return authorships


def add_authorship_definitions(root: etree._Element, auth_text_to_id: dict[str, int]) -> None:
    """
    Add authorship definitions to the XML root.

    Args:
        root: The XML root element
        auth_text_to_id: Dictionary mapping authorship text to IDs
    """
    auth_defs = []
    for auth_text, auth_id in auth_text_to_id.items():
        auth_def = etree.Element(
            "authorship",
            attrib={"id": f"authorship_{auth_id}"},
        )
        auth_child = etree.Element("author")
        auth_child.text = auth_text
        auth_def.append(auth_child)
        auth_defs.append(auth_def)
    for auth_def in reversed(auth_defs):
        root.insert(0, auth_def)


def remove_property_elements(res: etree._Element, properties: LegalProperties) -> None:
    """
    Remove text property elements from the resource XML.

    Args:
        res: The resource element
        properties: Configuration for property names to remove
    """
    if properties.authorship_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.authorship_prop}']"):
            res.remove(prop_elem)
    if properties.copyright_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.copyright_prop}']"):
            res.remove(prop_elem)
    if properties.license_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{properties.license_prop}']"):
            res.remove(prop_elem)


def apply_metadata_to_element(
    media_elem: etree._Element,
    license_val: str | None,
    copyright_val: str | None,
    authorships: list[str],
    auth_text_to_id: dict[str, int],
) -> None:
    """
    Apply valid metadata values as attributes on the media element.

    Args:
        media_elem: The bitstream or iiif-uri element
        license_val: The license value (or None)
        copyright_val: The copyright value (or None)
        authorships: List of authorship values
        auth_text_to_id: Dictionary to track unique authorships
    """
    if license_val and not is_fixme_value(license_val):
        media_elem.attrib["license"] = license_val
    if copyright_val and not is_fixme_value(copyright_val):
        media_elem.attrib["copyright-holder"] = copyright_val
    if authorships and not is_fixme_value(authorships[0]):
        # Use first authorship for the attribute
        first_auth = authorships[0]
        if (auth_id := auth_text_to_id.get(first_auth)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[first_auth] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"


def resolve_metadata_values(
    res: etree._Element,
    properties: LegalProperties,
    defaults: MetadataDefaults,
    csv_metadata: LegalMetadata | None,
    media_elem: etree._Element,
    auth_text_to_id: dict[str, int],
) -> tuple[str | None, str | None, list[str], str]:
    """
    Resolve metadata values using priority: CSV > XML > defaults.

    Args:
        res: The resource element
        properties: Configuration for property names
        defaults: Default values to use
        csv_metadata: Corrections from CSV file
        media_elem: The bitstream or iiif-uri element
        auth_text_to_id: Dictionary to track unique authorships

    Returns:
        Tuple of (license_val, copyright_val, authorships, file_val)
    """
    # Start with CSV corrections if available
    if csv_metadata:
        license_val = csv_metadata.license
        copyright_val = csv_metadata.copyright
        authorships = csv_metadata.authorships.copy()
        file_val = csv_metadata.multimedia_filepath
    else:
        license_val = None
        copyright_val = None
        authorships = []
        file_val = str(media_elem.text).strip() if media_elem.text else ""

    # Collect license (CSV > XML > default > None)
    if license_val is None and properties.license_prop:
        license_val = extract_license_from_xml(res, properties.license_prop)
    if license_val is None and defaults.license_default:
        license_val = apply_license_default(defaults.license_default)

    # Collect copyright (CSV > XML > default > None)
    if copyright_val is None and properties.copyright_prop:
        copyright_val = extract_copyright_from_xml(res, properties.copyright_prop)
    if copyright_val is None and defaults.copyright_default:
        copyright_val = defaults.copyright_default

    # Collect authorship (CSV > XML > default > None)
    if not authorships and properties.authorship_prop:
        authorships = extract_authorships_from_xml(res, properties.authorship_prop)
    if not authorships and defaults.authorship_default:
        authorships = [defaults.authorship_default]
        # Add to authorship definitions
        if (auth_id := auth_text_to_id.get(defaults.authorship_default)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[defaults.authorship_default] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"

    return license_val, copyright_val, authorships, file_val


def update_one_xml_resource(
    res: etree._Element,
    media_elem: etree._Element,
    properties: LegalProperties,
    defaults: MetadataDefaults,
    csv_metadata: LegalMetadata | None,
    auth_text_to_id: dict[str, int],
) -> LegalMetadata:
    """
    Collect legal metadata for a resource from CSV, XML properties, or defaults, then apply to media element.
    Priority order: CSV corrections > XML properties > defaults > None.
    The resource is updated in-place, and the collected metadata is returned for further processing.

    Args:
        res: The resource element
        media_elem: The bitstream or iiif-uri element
        properties: Configuration for property names to extract from XML
        defaults: Default values to use when metadata is missing
        csv_metadata: Corrections from CSV file
        auth_text_to_id: Dictionary to track unique authorships

    Returns:
        LegalMetadata with collected values
    """
    # Resolve metadata values using priority: CSV > XML > defaults
    license_val, copyright_val, authorships, file_val = resolve_metadata_values(
        res=res,
        properties=properties,
        defaults=defaults,
        csv_metadata=csv_metadata,
        media_elem=media_elem,
        auth_text_to_id=auth_text_to_id,
    )

    # Apply valid values to the media element
    apply_metadata_to_element(
        media_elem=media_elem,
        license_val=license_val,
        copyright_val=copyright_val,
        authorships=authorships,
        auth_text_to_id=auth_text_to_id,
    )

    # Remove the text properties from XML (they're now attributes on media element)
    remove_property_elements(res, properties)

    return LegalMetadata(
        multimedia_filepath=file_val,
        license=license_val,
        copyright=copyright_val,
        authorships=authorships,
    )
