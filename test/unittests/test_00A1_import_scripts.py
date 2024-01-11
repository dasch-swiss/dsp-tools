import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
import regex
from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.shared import check_notna


@pytest.fixture(scope="module")
def generated_xml_file() -> Iterator[Path]:
    """Yield the generated XML file as fixture, and delete it afterwards"""
    xml_file = Path("src/dsp_tools/import_scripts/data-processed.xml")
    yield xml_file
    xml_file.unlink(missing_ok=True)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_script(generated_xml_file: Path) -> None:
    """Execute the import script in its directory"""
    # pull the latest state of the git submodule
    subprocess.run("git submodule update --init --recursive".split(), check=True)
    from dsp_tools.import_scripts import import_script

    # execute the import script in its directory
    old_working_directory = os.getcwd()
    os.chdir("src/dsp_tools/import_scripts")
    try:
        import_script.main()
    finally:
        os.chdir(old_working_directory)

    # check the output XML
    with open("testdata/excel2xml/00A1-data-processed-expected.xml", encoding="utf-8") as f:
        xml_expected = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
    with open(generated_xml_file, encoding="utf-8") as f:
        xml_returned = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
    assert _sort_xml_by_id(xml_expected) == _sort_xml_by_id(xml_returned)


def _sort_xml_by_id(xml: str) -> str:
    """Sort the elements in the XML by their ID"""
    xml_tree = etree.fromstring(xml.encode("utf-8"))
    for elem in xml_tree.iter():
        elem[:] = sorted(elem, key=lambda x: x.attrib.get("id", ""))
    return etree.tostring(xml_tree).decode("utf-8")


def _derandomize_xsd_id(
    string: str,
    multiple_occurrences: bool = False,
) -> str:
    """
    In some contexts, the random component of the output of make_xsd_id_compatible() is a hindrance,
    especially for testing.
    This method removes the random part,
    but leaves the other modifications introduced by make_xsd_id_compatible() in place.
    This method's behaviour is defined by the example in the "Examples" section.

    Args:
        string: the output of make_xsd_id_compatible()
        multiple_occurrences: If true, string can be an entire XML document, and all occurrences will be removed

    Raises:
        BaseError: if the input cannot be derandomized

    Returns:
        the derandomized string

    Examples:
        >>> id_1 = make_xsd_id_compatible("Hello!")
        >>> id_2 = make_xsd_id_compatible("Hello!")
        >>> assert _derandomize_xsd_id(id_1) == _derandomize_xsd_id(id_2)
    """
    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be derandomized.")

    uuid4_regex = r"[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
    if multiple_occurrences:
        return regex.subn(uuid4_regex, "", string, flags=regex.IGNORECASE)[0]
    else:
        return regex.sub(uuid4_regex, "", string, regex.IGNORECASE)


if __name__ == "__main__":
    pytest.main([__file__])
