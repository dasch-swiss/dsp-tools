# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from termcolor import cprint

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xmlupload.stash_circular_references import remove_circular_references
from dsp_tools.utils.xmlupload.xmlupload import _extract_resources_from_xml


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file("testdata/xml-data/circular-references/test_circular_references_1.xml")
    resources = _extract_resources_from_xml(test_root, "simcir")
    ok_resources, stash = remove_circular_references(resources, False)
    stashed_links = len(stash.standoff_stash.res_2_stash_items) + len(stash.link_value_stash.res_2_stash_items)
    print_str = (
        f"\n\n---------------------\n"
        f"Total Resources: 63\n"
        f"Previous Stash Size: 32\n"
        f"Current Stash Size: {stashed_links}"
        f"\n---------------------\n"
    )
    cprint(text=print_str, color="yellow", attrs=["bold"])
    assert stashed_links <= 32


if __name__ == "__main__":
    pytest.main([__file__])
