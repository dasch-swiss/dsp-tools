# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xmlupload.stash_circular_references import remove_circular_references
from dsp_tools.utils.xmlupload.xmlupload import _extract_resources_from_xml


def test_check_if_number_ok_links_increases_stashes_decrease() -> None:
    test_root = parse_and_clean_xml_file("testdata/generate_test_data/test_circular_references_1.xml")
    resources = _extract_resources_from_xml(test_root, "simcir")
    ok_resources, _, _ = remove_circular_references(resources, False)
    assert len(ok_resources) >= 26


if __name__ == "__main__":
    pytest.main([__file__])
