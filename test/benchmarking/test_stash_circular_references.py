from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _extract_resources_from_xml
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_xmlresource_into_intermediary_classes import (
    transform_xmlresources_into_intermediary_resources,
)
from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.create_info_for_graph import create_info_for_graph_from_intermediary_resources
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW
from dsp_tools.utils.xml_parsing.parse_and_transform import parse_and_clean_xml_file


def test_get_length_ok_resources() -> None:
    test_root = parse_and_clean_xml_file(Path("testdata/xml-data/test-circular-references.xml"))
    resources = _extract_resources_from_xml(test_root, "simcir")
    permissions_lookup = {"open": Permissions()}
    intermediary_lookups = IntermediaryLookups(
        permissions_lookup, {}, namespaces={"simcir": "https://namespace.ch/simcir#"}, authorships={}
    )
    transformation_result = transform_xmlresources_into_intermediary_resources(resources, intermediary_lookups)
    info_for_graph = create_info_for_graph_from_intermediary_resources(transformation_result.transformed_resources)
    stash_lookup, _ = generate_upload_order(info_for_graph)
    stash = stash_circular_references(transformation_result.transformed_resources, stash_lookup)
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
