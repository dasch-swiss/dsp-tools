from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from lxml import etree

from dsp_tools.commands.update_legal.core import update_legal_metadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties


@pytest.fixture
def output_files() -> Iterator[tuple[Path, Path]]:
    generated_csv = Path("testdata/xml-data/test_update_legal_input_legal_errors.csv")
    generated_xml = Path("testdata/xml-data/test_update_legal_input_PARTIALLY_updated.xml")

    yield generated_csv, generated_xml

    if generated_csv.exists():
        generated_csv.unlink()
    if generated_xml.exists():
        generated_xml.unlink()


def test_update_legal_with_errors(output_files: tuple[Path, Path]) -> None:
    """
    Test the update-legal command with an XML file containing some errors.

    This test verifies that:
    - Valid resources are converted correctly
    - Resources with errors remain unchanged
    - An error CSV file is generated with the expected errors
    - A partially updated XML file is generated
    """
    generated_csv, generated_xml = output_files
    input_xml = Path("testdata/xml-data/test_update_legal_input.xml")
    expected_csv = Path("testdata/xml-data/test_update_legal_errors_expected.csv")
    expected_xml = Path("testdata/xml-data/test_update_legal_output_expected.xml")

    properties = LegalProperties(
        authorship_prop=":hasAuthorship",
        copyright_prop=":hasCopyright",
        license_prop=":hasLicense",
    )
    defaults = LegalMetadataDefaults()

    result = update_legal_metadata(
        input_file=input_xml,
        properties=properties,
        defaults=defaults,
    )

    assert not result  # there are errors
    assert generated_csv.exists()
    assert generated_xml.exists()

    # Compare the generated CSV with the expected CSV (Sort both DataFrames by resource_id for consistent comparison)
    generated_csv_df = pd.read_csv(generated_csv)
    expected_csv_df = pd.read_csv(expected_csv)
    generated_csv_df = generated_csv_df.sort_values(by="resource_id").reset_index(drop=True)
    expected_csv_df = expected_csv_df.sort_values(by="resource_id").reset_index(drop=True)
    pd.testing.assert_frame_equal(generated_csv_df, expected_csv_df)

    # Compare the generated XML with the expected XML
    generated_tree = etree.parse(generated_xml)
    expected_tree = etree.parse(expected_xml)

    # Remove whitespace for comparison
    etree.indent(generated_tree, space="")
    etree.indent(expected_tree, space="")

    generated_str = etree.tostring(generated_tree, encoding="unicode")
    expected_str = etree.tostring(expected_tree, encoding="unicode")

    assert generated_str == expected_str


if __name__ == "__main__":
    pytest.main([__file__])
