from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.stash.stash_circular_references import identify_circular_references
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.xmlupload import _extract_resources_from_xml
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file

# ANSI Color (see custom_warnings.py for more details)
SEQUENCE_END = "m"
SEQUENCE_START = "\u001b["
YELLOW = f"{SEQUENCE_START}1;33{SEQUENCE_END}"  # 1 (bold) ; 33 (yellow)
RESET_TO_DEFAULT = f"{SEQUENCE_START}0{SEQUENCE_END}"  # reset to the default setting of the console


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file(Path("testdata/xml-data/circular-references/test_circular_references_1.xml"))
    stash_lookup, _ = identify_circular_references(test_root)
    resources = _extract_resources_from_xml(test_root, "simcir")
    stash = stash_circular_references(resources, stash_lookup, {"open": Permissions()})
    len_standoff = len(stash.standoff_stash.res_2_stash_items)  # type: ignore[union-attr]
    len_resptr = len(stash.link_value_stash.res_2_stash_items)  # type: ignore[union-attr]
    stashed_links = len_standoff + len_resptr
    previous_stash_size = 14
    print_str = (
        f"\n\n---------------------\n"
        f"Total Resources: 63\n"
        f"Previous Stash Size: {previous_stash_size}\n"
        f"Current Stash Size: {stashed_links}"
        f"\n---------------------\n"
    )
    print(YELLOW + print_str + RESET_TO_DEFAULT)
    assert stashed_links <= previous_stash_size


if __name__ == "__main__":
    pytest.main([__file__])
