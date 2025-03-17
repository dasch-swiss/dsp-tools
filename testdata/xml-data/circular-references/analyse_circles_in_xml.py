from datetime import datetime
from pathlib import Path

from viztracer import VizTracer

from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import _generate_upload_order_from_graph
from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import _make_graph
from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import create_info_from_xml_for_graph
from dsp_tools.utils.xml_parsing.parse_and_transform import parse_and_clean_xml_file


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
    root = parse_and_clean_xml_file(xml_filepath)
    graph_info = create_info_from_xml_for_graph(root)
    tracer: VizTracer | None = None
    if save_tracer:
        tracer = VizTracer(
            minimize_memory=True,
            max_stack_depth=3,
        )
        tracer.start()
    start = datetime.now()
    print("=" * 80)
    print(f"Total Number of Resources: {len(graph_info.all_resource_ids)}")
    print(f"Total Number of resptr Links: {len(graph_info.link_values)}")
    print(f"Total Number of XML Texts with Links: {len(graph_info.standoff_links)}")
    print("=" * 80)
    graph, node_to_id, edges = _make_graph(graph_info)
    _, _, stash_counter = _generate_upload_order_from_graph(graph, node_to_id, edges)
    end = datetime.now()
    if save_tracer and tracer:
        tracer.stop()
        tracer.save(output_file=tracer_output_file)
    print("Number of Links Stashed:", stash_counter)
    print("=" * 80)
    print("Start time:", start)
    print("End time:", end)
    print("Duration:", end - start)
    print("=" * 80)


if __name__ == "__main__":
    analyse_circles_in_data(
        xml_filepath=Path("testdata/xml-data/circular-references/test_circular_references_1.xml"),
        tracer_output_file="circular_references_tracer.json",
        save_tracer=False,
    )
