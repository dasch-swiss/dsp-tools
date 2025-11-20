from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _transform_into_localnames
from dsp_tools.xmllib.general_functions import find_license_in_string


@dataclass(frozen=True)
class Problem:
    """
    Represents a problem with legal metadata for a single resource.

    Attributes:
        file: The multimedia file path referenced by the resource
        res_id: The resource ID
        license: The license value or FIXME marker
        copyright: The copyright value or FIXME marker
        authorships: List of authorship values, or FIXME marker in first position
    """

    file: str
    res_id: str
    license: str
    copyright: str
    authorships: list[str]

    def execute_error_protocol(self) -> str:
        """Format problem as human-readable string for console output."""
        parts = [f"Resource ID: {self.res_id}", f"File: {self.file}"]

        if self.license.startswith("FIXME:"):
            parts.append(f"License: {self.license}")
        if self.copyright.startswith("FIXME:"):
            parts.append(f"Copyright: {self.copyright}")
        if self.authorships and self.authorships[0].startswith("FIXME:"):
            parts.append(f"Authorship: {self.authorships[0]}")

        return " | ".join(parts)


@dataclass(frozen=True)
class ProblemAggregator:
    """
    Aggregates multiple problems and provides DataFrame export for CSV generation.
    """

    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        """Format all problems as human-readable string for console output."""
        msg = "The legal metadata in your XML file contains the following problems:\n\n" + "\n - ".join(
            [x.execute_error_protocol() for x in self.problems]
        )
        return msg

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert problems to DataFrame for CSV export.

        Follows the pattern from validate-data command.
        """
        # Build list of dicts with user-facing column names
        problem_dicts = []
        for problem in self.problems:
            # Start with base columns
            row_dict = {
                "file": problem.file,
                "resource_id": problem.res_id,
                "license": problem.license,
                "copyright": problem.copyright,
            }

            # Add authorship columns (authorship_1, authorship_2, etc.)
            for i, authorship in enumerate(problem.authorships, start=1):
                row_dict[f"authorship_{i}"] = authorship

            problem_dicts.append(row_dict)

        # Create DataFrame from records (same method as validate-data)
        df = pd.DataFrame.from_records(problem_dicts)

        # Sort by resource ID for consistency
        df = df.sort_values(by=["resource_id"])

        return df

    def save_to_csv(self, input_file: Path) -> Path:
        """
        Save problems to CSV file.

        Follows the pattern from validate-data command.

        Args:
            input_file: The input XML file path

        Returns:
            Path to the created CSV file
        """
        # Construct output path: {input_stem}_legal_errors.csv
        output_path = input_file.parent / f"{input_file.stem}_legal_errors.csv"

        # Convert to DataFrame and save (index=False as per validate-data pattern)
        df = self.to_dataframe()
        df.to_csv(output_path, index=False)

        return output_path


@dataclass(frozen=True)
class LegalMetadata:
    """
    Represents legal metadata for a single resource, either from XML or CSV.

    Attributes:
        file: The multimedia file path
        license: The license value (or None if missing)
        copyright: The copyright holder (or None if missing)
        authorships: List of authorship values (empty list if missing)
    """

    file: str
    license: str | None
    copyright: str | None
    authorships: list[str]


def _read_corrections_csv(csv_path: Path) -> dict[str, LegalMetadata]:
    """
    Read corrected legal metadata from a CSV file.

    Args:
        csv_path: Path to the CSV file with corrected values

    Returns:
        Dictionary mapping resource_id to LegalMetadata

    Raises:
        InputError: If CSV file cannot be read or has invalid format
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        msg = f"Could not read CSV file '{csv_path}': {e}"
        raise InputError(msg) from e

    # Validate required columns
    required_cols = {"file", "resource_id", "license", "copyright"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        msg = f"CSV file is missing required columns: {missing}"
        raise InputError(msg)

    corrections = {}
    for _, row in df.iterrows():
        res_id = str(row["resource_id"])

        # Skip rows that still have FIXME markers (not yet corrected)
        license_val = str(row["license"]) if pd.notna(row["license"]) else None
        copyright_val = str(row["copyright"]) if pd.notna(row["copyright"]) else None

        if license_val and license_val.startswith("FIXME:"):
            license_val = None
        if copyright_val and copyright_val.startswith("FIXME:"):
            copyright_val = None

        # Collect all authorship columns (authorship_1, authorship_2, etc.)
        authorships = []
        i = 1
        while f"authorship_{i}" in df.columns:
            auth_val = row[f"authorship_{i}"]
            if pd.notna(auth_val):
                auth_str = str(auth_val)
                # Skip FIXME markers
                if not auth_str.startswith("FIXME:"):
                    authorships.append(auth_str)
            i += 1

        corrections[res_id] = LegalMetadata(
            file=str(row["file"]),
            license=license_val,
            copyright=copyright_val,
            authorships=authorships,
        )

    return corrections


def update_legal_metadata(
    input_file: Path,
    auth_prop: str | None = None,
    copy_prop: str | None = None,
    license_prop: str | None = None,
    auth_default: str | None = None,
    copy_default: str | None = None,
    license_default: str | None = None,
    fixed_errors_file: Path | None = None,
) -> bool:
    """
    Update legal metadata in an XML file, converting text properties to bitstream attributes.

    Args:
        input_file: Path to the input XML file
        auth_prop: Property name for authorship (e.g., ':hasAuthor')
        copy_prop: Property name for copyright (e.g., ':hasCopyright')
        license_prop: Property name for license (e.g., ':hasLicense')
        auth_default: Default authorship value when missing
        copy_default: Default copyright value when missing
        license_default: Default license value when missing
        fixed_errors_file: Path to CSV file with corrected values

    Returns:
        True if XML was successfully written, False if CSV error file was created
    """
    # Load CSV corrections if provided
    csv_corrections = None
    if fixed_errors_file:
        csv_corrections = _read_corrections_csv(fixed_errors_file)

    # Parse and update XML
    root = _parse_xml_file(input_file)
    root = _transform_into_localnames(root)

    root_updated, problems = _update(
        root=root,
        auth_prop=auth_prop,
        copy_prop=copy_prop,
        license_prop=license_prop,
        auth_default=auth_default,
        copy_default=copy_default,
        license_default=license_default,
        csv_corrections=csv_corrections,
    )

    # If there are problems, create CSV error file and don't write XML
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


def _update(
    root: etree._Element,
    auth_prop: str | None = None,
    copy_prop: str | None = None,
    license_prop: str | None = None,
    auth_default: str | None = None,
    copy_default: str | None = None,
    license_default: str | None = None,
    csv_corrections: dict[str, LegalMetadata] | None = None,
) -> tuple[etree._Element, list[Problem]]:
    """
    Update the XML tree with legal metadata, applying corrections and defaults.

    Args:
        root: The XML root element
        auth_prop: Property name for authorship (or None)
        copy_prop: Property name for copyright (or None)
        license_prop: Property name for license (or None)
        auth_default: Default authorship value (or None)
        copy_default: Default copyright value (or None)
        license_default: Default license value (or None)
        csv_corrections: Dictionary of corrections from CSV (or None)

    Returns:
        Tuple of (updated root element, list of problems)
    """
    if not any([auth_prop, copy_prop, license_prop]):
        raise InputError("At least one of auth_prop, copy_prop, license_prop must be provided")

    auth_text_to_id: dict[str, int] = {}
    problems: list[Problem] = []

    # Process each resource with multimedia
    for res in root.iterchildren(tag="resource"):
        if not (media_tag_candidates := res.xpath("bitstream|iiif-uri")):
            continue

        res_id = res.attrib["id"]
        media_elem = media_tag_candidates[0]
        media_file = str(media_elem.text).strip() if media_elem.text else ""

        # Get metadata from CSV corrections (highest priority)
        csv_metadata = csv_corrections.get(res_id) if csv_corrections else None

        # Collect metadata from XML and apply to the resource
        metadata = _collect_metadata_for_resource(
            res=res,
            media_elem=media_elem,
            auth_prop=auth_prop,
            copy_prop=copy_prop,
            license_prop=license_prop,
            auth_default=auth_default,
            copy_default=copy_default,
            license_default=license_default,
            csv_metadata=csv_metadata,
            auth_text_to_id=auth_text_to_id,
        )

        # Check if there are any problems (missing or invalid values)
        if _has_problems(metadata):
            problem = Problem(
                file=media_file,
                res_id=res_id,
                license=metadata.license or "FIXME: License missing",
                copyright=metadata.copyright or "FIXME: Copyright missing",
                authorships=metadata.authorships if metadata.authorships else ["FIXME: Authorship missing"],
            )
            problems.append(problem)

    # Add authorship definitions to the XML
    if auth_text_to_id:
        _add_auth_defs(root, auth_text_to_id)

    return root, problems


def _has_problems(metadata: LegalMetadata) -> bool:
    """
    Check if metadata has any missing or invalid fields that should be reported in CSV.

    Args:
        metadata: The legal metadata to check

    Returns:
        True if there are problems, False otherwise
    """
    # Check if any required field is missing
    has_license_problem = metadata.license is None or metadata.license.startswith("FIXME:")
    has_copyright_problem = metadata.copyright is None or metadata.copyright.startswith("FIXME:")
    has_authorship_problem = not metadata.authorships or (
        bool(metadata.authorships) and metadata.authorships[0].startswith("FIXME:")
    )

    return has_license_problem or has_copyright_problem or has_authorship_problem


def _collect_metadata_for_resource(
    res: etree._Element,
    media_elem: etree._Element,
    auth_prop: str | None,
    copy_prop: str | None,
    license_prop: str | None,
    auth_default: str | None,
    copy_default: str | None,
    license_default: str | None,
    csv_metadata: LegalMetadata | None,
    auth_text_to_id: dict[str, int],
) -> LegalMetadata:
    """
    Collect legal metadata for a resource from CSV, XML properties, or defaults.

    Priority order: CSV corrections > XML properties > defaults > None

    Args:
        res: The resource element
        media_elem: The bitstream or iiif-uri element
        auth_prop: Property name for authorship
        copy_prop: Property name for copyright
        license_prop: Property name for license
        auth_default: Default authorship value
        copy_default: Default copyright value
        license_default: Default license value
        csv_metadata: Corrections from CSV file
        auth_text_to_id: Dictionary to track unique authorships

    Returns:
        LegalMetadata with collected values
    """
    # Start with CSV corrections if available
    if csv_metadata:
        license_val = csv_metadata.license
        copyright_val = csv_metadata.copyright
        authorships = csv_metadata.authorships.copy()
        file_val = csv_metadata.file
    else:
        license_val = None
        copyright_val = None
        authorships = []
        file_val = str(media_elem.text).strip() if media_elem.text else ""

    # Collect license (CSV > XML > default > None)
    if license_val is None and license_prop:
        license_val = _extract_license_from_xml(res, license_prop)
    if license_val is None and license_default:
        license_val = _apply_license_default(license_default)

    # Collect copyright (CSV > XML > default > None)
    if copyright_val is None and copy_prop:
        copyright_val = _extract_copyright_from_xml(res, copy_prop)
    if copyright_val is None and copy_default:
        copyright_val = copy_default

    # Collect authorship (CSV > XML > default > None)
    if not authorships and auth_prop:
        authorships = _extract_authorships_from_xml(res, auth_prop)
    if not authorships and auth_default:
        authorships = [auth_default]
        # Add to authorship definitions
        if (auth_id := auth_text_to_id.get(auth_default)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[auth_default] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"

    # Apply valid values to the media element
    if license_val and not license_val.startswith("FIXME:"):
        media_elem.attrib["license"] = license_val
    if copyright_val and not copyright_val.startswith("FIXME:"):
        media_elem.attrib["copyright-holder"] = copyright_val
    if authorships and not authorships[0].startswith("FIXME:"):
        # Use first authorship for the attribute
        first_auth = authorships[0]
        if (auth_id := auth_text_to_id.get(first_auth)) is None:
            auth_id = len(auth_text_to_id)
            auth_text_to_id[first_auth] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"

    # Remove the text properties from XML (they're now attributes on media element)
    if auth_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{auth_prop}']"):
            res.remove(prop_elem)
    if copy_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{copy_prop}']"):
            res.remove(prop_elem)
    if license_prop:
        for prop_elem in res.xpath(f"./text-prop[@name='{license_prop}']"):
            res.remove(prop_elem)

    return LegalMetadata(
        file=file_val,
        license=license_val,
        copyright=copyright_val,
        authorships=authorships,
    )


def _extract_license_from_xml(res: etree._Element, license_prop: str) -> str | None:
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


def _apply_license_default(license_default: str) -> str | None:
    """Apply default license value, parsing it if possible."""
    if not (lic := find_license_in_string(license_default)):
        # Unknown license - mark as FIXME
        return f"FIXME: Invalid license: {license_default}"
    return lic.value


def _extract_copyright_from_xml(res: etree._Element, copy_prop: str) -> str | None:
    """Extract copyright from XML property."""
    copy_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{copy_prop}']/text")
    if not copy_elems:
        return None
    # Use first element if multiple exist
    copy_elem = copy_elems[0]
    if not copy_elem.text or not (copy_text := copy_elem.text.strip()):
        return None
    return copy_text


def _extract_authorships_from_xml(res: etree._Element, auth_prop: str) -> list[str]:
    """Extract authorships from XML property."""
    auth_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{auth_prop}']/text")
    if not auth_elems:
        return []

    authorships = []
    for auth_elem in auth_elems:
        if auth_elem.text and (auth_text := auth_elem.text.strip()):
            authorships.append(auth_text)

    return authorships


def _add_auth_defs(root: etree._Element, auth_text_to_id: dict[str, int]) -> None:
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
