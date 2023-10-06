from pathlib import Path
from typing import Any

from lxml import etree

from dsp_tools import excel2xml


def create_and_save_circular_references_test_graph(replication_counter: int = 1, save_location: str = "") -> None:
    """
    This function creates a graph with circular references.
    By default, it saves it in the current directory; this can be changed with the parameter save_location.

    Args:
        replication_counter: number of times the sub-graphs should be created in one root-graph.
        save_location: path to the folder, where the file should be saved
    """
    root = create_circular_references_test_graph(replication_counter=replication_counter)
    excel2xml.write_xml(root, Path(save_location / f"test_circular_references_{replication_counter}.xml"))


def create_circular_references_test_graph(replication_counter: int) -> etree._Element:
    """
    This function creates a graph with circular references.
    It is capable of reproducing one graph with all the references a specified number of times.
    Each circle type has its own sub-graph number in order to differentiate them by their ID.
    The resulting etree is suitable for an upload to the DSP-API.

    Args:
        replication_counter: number of times the sub-graphs should be created in one root-graph.

    Returns:
        A etree which is suitable for an upload into the DSP-API
    """
    root = excel2xml.make_root("9000", "simple")
    for i in range(1, replication_counter + 1):
        root.extend(_make_one_circle_with_three_resources(replication_counter=f"{i}1"))
        root.extend(_make_complex_dependencies(replication_counter=f"{i}2"))
        root.extend(_make_complex_dependencies_add_on(replication_counter=f"{i}3"))
        root.extend(_make_two_references(replication_counter=f"{i}4"))
        root.extend(_make_chain(replication_counter=f"{i}5"))
        root.extend(_make_inverted_complex_dependencies(replication_counter=f"{i}6"))
    return root


def _make_list_of_resources(number_of_resources: int, replication_counter: str, start_range: int = 65) -> list[Any]:
    letters = [chr(x) for x in range(start_range, start_range + number_of_resources)]
    return [
        excel2xml.make_resource(
            restype=":TestThing", label=f"res_{let}_{replication_counter}", id=f"res_{let}_{replication_counter}"
        )
        for let in letters
    ]


def _make_salsah_link(target_res: etree._Element) -> etree._Element:
    return f'<a class="salsah-link" href="IRI:{target_res.attrib["id"]}:IRI">{target_res.attrib["id"]}</a>'


def _make_xml_text_prop(target_res: etree._Element | list[etree._Element]) -> etree._Element:
    match target_res:
        case etree._Element():
            salsah_link = _make_salsah_link(target_res)
            # one resource with many targets
        case list():
            salsah_link = "".join([_make_salsah_link(x) for x in target_res])
    return excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))


def _make_resptr_prop(target_res: list[etree._Element] | etree._Element) -> etree._Element:
    match target_res:
        case etree._Element():
            link = excel2xml.make_resptr_prop(name=":hasResource", value=target_res.attrib["id"])
        # one resource with many targets
        case list():
            link = excel2xml.make_resptr_prop(name=":hasResource", value=[x.attrib["id"] for x in target_res])
    return link


def _make_simple_text(resource: etree._Element) -> etree._Element:
    resource.append(excel2xml.make_text_prop(name=":hasSimpleText", value="This is text."))
    return resource


def _make_chain(replication_counter: str) -> list[etree._Element]:
    # A -> B -> C -> D -> E (resptr-prop)

    resources = _make_list_of_resources(5, replication_counter)
    resptr = [_make_resptr_prop(x) for x in resources[1:]]
    for i, link in enumerate(resptr):
        resources[i].append(link)
    return resources


def _make_one_circle_with_three_resources(replication_counter: str) -> list[etree._Element]:
    # A -> B (xml-text) & (resptr-prop)
    # B -> C (xml-text) & (resptr-prop)
    # C -> A (xml-text) & (resptr-prop)

    res_li = _make_list_of_resources(number_of_resources=3, replication_counter=replication_counter)
    salsah_list = [_make_xml_text_prop(x) for x in res_li]
    resptr_list = [_make_resptr_prop(x) for x in res_li]
    res_li[0].append(salsah_list[1])
    res_li[0].append(resptr_list[1])
    res_li[1].append(salsah_list[2])
    res_li[1].append(resptr_list[2])
    res_li[2].append(salsah_list[0])
    res_li[2].append(resptr_list[0])
    return res_li


def _make_two_references(replication_counter: str) -> list[etree._Element]:
    # A -> B (resptr-prop)
    # B -> A (xml-text)

    res_li = _make_list_of_resources(2, replication_counter)
    res_li[0].append(_make_resptr_prop(res_li[1]))
    res_li[1].append(_make_xml_text_prop(res_li[0]))
    return res_li


def _make_complex_dependencies(replication_counter: str) -> list[etree._Element]:
    # A -> D (xml-text)
    # B -> D (xml-text)
    # C -> D (xml-text)
    # D -> E (resptr-prop)
    # E -> A / B / C (resptr-prop)

    all_resources = _make_list_of_resources(number_of_resources=5, replication_counter=replication_counter)
    all_resources = _make_complex_dependencies_resource_ABC(all_resources)
    all_resources = _make_complex_dependencies_resource_D(all_resources)
    return _make_complex_dependencies_resource_E(all_resources)


def _make_complex_dependencies_resource_ABC(resource_list: list[etree._Element]) -> list[etree._Element]:
    link_l = [_make_xml_text_prop(target_res=resource_list[3]) for i in range(3)]
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(_make_resptr_prop(resource_list[4]))
    return resource_list


def _make_complex_dependencies_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[4].append(_make_resptr_prop(target_res=resource_list[0:3]))
    return resource_list


def _make_complex_dependencies_add_on(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies
    # plus
    # D -> F (xml-text)
    # F -> E (resptr-prop)

    complex_dep_li = _make_complex_dependencies(replication_counter)
    f_id = f"res_F_{replication_counter}"
    f_res: etree._Element = excel2xml.make_resource(restype=":TestThing", label=f_id, id=f_id)
    s_link = _make_xml_text_prop(target_res=f_res)
    f_res.append(_make_resptr_prop(complex_dep_li[-1]))
    complex_dep_li[3].append(s_link)
    complex_dep_li.append(f_res)
    return complex_dep_li


def _make_complex_dependencies_with_simpletext(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies
    # plus each value has a simple text property

    complex_dep_li = _make_complex_dependencies(replication_counter)
    return [_make_simple_text(x) for x in complex_dep_li]


def _make_inverted_complex_dependencies(replication_counter: str) -> list[etree._Element]:
    # A -> D (resptr-prop)
    # B -> D (resptr-prop)
    # C -> D (resptr-prop)
    # D -> E (xml-text)
    # E -> A / B / C (xml-text)

    all_resources = _make_list_of_resources(number_of_resources=5, replication_counter=replication_counter)
    all_resources = _make_inverted_complex_dependencies_resource_ABC(all_resources)
    all_resources = _make_inverted_complex_dependencies_resource_D(all_resources)
    return _make_inverted_complex_dependencies_resource_E(all_resources)


def _make_inverted_complex_dependencies_resource_ABC(resource_list: list[etree._Element]) -> list[etree._Element]:
    link_l = [_make_resptr_prop(target_res=resource_list[3]) for i in range(3)]
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_inverted_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(_make_xml_text_prop(resource_list[4]))
    return resource_list


def _make_inverted_complex_dependencies_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[4].append(_make_xml_text_prop(target_res=resource_list[0:3]))
    return resource_list
