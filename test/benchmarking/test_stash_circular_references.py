from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _get_intermediary_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file(Path("testdata/xml-data/test-circular-references.xml"))
    parsed_resources, _ = get_parsed_resources(test_root, "https://namespace.ch/")
    permissions_lookup = {"open": Permissions()}
    intermediary_lookups = IntermediaryLookups(
        permissions_lookup, {}, namespaces={"simcir": "https://namespace.ch/simcir#"}, authorships={}
    )
    intermediary_resources = _get_intermediary_resources(parsed_resources, intermediary_lookups)
    _, stash = get_stash_and_upload_order(intermediary_resources)
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
