from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file(Path("testdata/xml-data/test-circular-references.xml"))
    parsed_resources = get_parsed_resources(test_root, "https://namespace.ch/")
    permissions_lookup = {"public": Permissions()}
    xml_lookups = XmlReferenceLookups(permissions_lookup, {}, authorships={})
    processed_resources = get_processed_resources(parsed_resources, xml_lookups, is_on_prod_like_server=False)
    _, stash = get_stash_and_upload_order(processed_resources)
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
