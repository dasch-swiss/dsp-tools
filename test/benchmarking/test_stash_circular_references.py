# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from termcolor import cprint

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xmlupload.stash_circular_references import remove_circular_references
from dsp_tools.utils.xmlupload.xmlupload import _extract_resources_from_xml


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file("testdata/xml-data/circular-references/test_circular_references_1.xml")
    resources = _extract_resources_from_xml(test_root, "simcir")
    ok_resources, _, _ = remove_circular_references(resources, False)
    print_str = (
        f"\n\n---------------------\n"
        f"Original length: 36\n"
        f"New length: {len(ok_resources)}"
        f"\n---------------------\n"
    )
    cprint(text=print_str, color="yellow", attrs=["bold"])
    assert len(ok_resources) >= 36


if __name__ == "__main__":
    pytest.main([__file__])
