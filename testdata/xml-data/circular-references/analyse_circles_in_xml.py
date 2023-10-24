from datetime import datetime
from pathlib import Path

from lxml import etree
from viztracer import VizTracer

from dsp_tools.analyse_xml_data.construct_and_analyze_graph import (
    create_info_from_xml_for_graph,
    generate_upload_order,
    make_graph,
)


def analyse_circles_in_data(xml_filepath: Path, tracer_output_file: str, save_tracer: bool = False) -> None:
    """
    This function takes an XML filepath
    It analyzes how many and which links have to be removed
    so that all circular references are broken up.
    This is for analysis purposes only.

    Args:
        xml_filepath: path to the file
        tracer_output_file: name of the file where the viztracer results should be saved
        save_tracer: True if the output of the viztracer should be saved
    """
    start = datetime.now()
    print("=" * 80)
    tracer = VizTracer(
        minimize_memory=True,
        max_stack_depth=3,
    )
    tracer.start()
    tree = etree.parse(xml_filepath)
    root = tree.getroot()
    resptr_links, xml_links, all_resource_ids = create_info_from_xml_for_graph(root)
    print(f"Total Number of Resources: {len(all_resource_ids)}")
    print(f"Total Number of resptr Links: {len(resptr_links)}")
    print(f"Total Number of XML Texts with Links: {len(xml_links)}")
    print("=" * 80)
    graph, rustworkx_index_to_id, edges = make_graph(resptr_links, xml_links, all_resource_ids)
    _, _, stash_counter = generate_upload_order(graph, rustworkx_index_to_id, edges)
    print("Number of Links Stashed:", stash_counter)
    tracer.stop()
    if save_tracer:
        tracer.save(output_file=tracer_output_file)
    print("=" * 80)
    print("Start time:", start)
    print("End time:", datetime.now())
    print("=" * 80)


if __name__ == "__main__":
    analyse_circles_in_data(
        xml_filepath=Path("testdata/xml-data/circular-references/test_circular_references_1.xml"),
        tracer_output_file="circular_references_tracer.json",
        save_tracer=False,
    )
