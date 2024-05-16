from pathlib import Path
from typing import Any

from lxml import etree

from dsp_tools import excel2xml


def create_and_save_circular_references_test_graph(replication_counter: int = 1, save_location: str = "") -> None:
    """
    This function creates a graph with circular references.
    By default, it saves it in the current directory; this can be changed with the parameter save_location.

    Args:
        replication_counter: number of times the sub-graphs should be created in one root-graph
        save_location: path to the folder, where the file should be saved
    """
    root = excel2xml.make_root("0700", "simcir")
    root = create_circular_references_test_graph(root, replication_counter)
    excel2xml.write_xml(root, Path(save_location) / f"test_circular_references_{replication_counter}.xml")


def create_circular_references_test_graph(root: etree._Element, replication_counter: int) -> etree._Element:
    """
    This function creates a graph with circular references.
    It is capable of reproducing one graph with all the references a specified number of times.
    Each circle type has its own sub-graph number in order to differentiate them by their ID.
    The resulting etree is suitable for an upload to the DSP-API.

    Args:
        root: root of the XML
        replication_counter: number of times the sub-graphs should be created in one root-graph.

    Returns:
        An etree which is suitable for an upload into the DSP-API
    """
    for i in range(1, replication_counter + 1):
        root.extend(_make_one_circle_with_three_resources(replication_counter=f"{i}1"))
        root.extend(_make_complex_dependencies_single_link(replication_counter=f"{i}2.1"))
        root.extend(_make_complex_circular_dependencies_multi_link(replication_counter=f"{i}2.2"))
        root.extend(_make_complex_dependencies_add_on(replication_counter=f"{i}3"))
        root.extend(_make_two_references(replication_counter=f"{i}4.1"))
        root.extend(_make_multi_link_two_resource_circle(replication_counter=f"{i}4.2"))
        root.extend(_make_chain(replication_counter=f"{i}5"))
        root.extend(_make_inverted_complex_dependencies(replication_counter=f"{i}6"))
        root.extend(_make_two_resource_circle_plus_non_circle_link(replication_counter=f"{i}7"))
        root.extend(_make_three_resource_circle_with_multiple_text_prop(replication_counter=f"{i}8"))
        root.extend(_make_three_resource_circle_multiple_diverse_links(replication_counter=f"{i}9"))
        root.extend(_make_complex_circle_with_leaf_nodes(replication_counter=f"{i}10"))
    return root


def _make_list_of_resources(number_of_resources: int, replication_counter: str, start_range: int = 65) -> list[Any]:
    letters = [chr(x) for x in range(start_range, start_range + number_of_resources)]
    return [
        excel2xml.make_resource(
            restype=":TestThing", label=f"res_{let}_{replication_counter}", id=f"res_{let}_{replication_counter}"
        )
        for let in letters
    ]


def _make_salsah_link(target_id: str) -> str:
    return f'<a class="salsah-link" href="IRI:{target_id}:IRI">{target_id}</a>'


def _make_xml_text_prop(target_res: etree._Element | list[etree._Element]) -> etree._Element:
    match target_res:
        case etree._Element():
            salsah_link = _make_salsah_link(target_res.attrib["id"])
            # one resource with many targets
        case list():
            salsah_link = "blabla".join([_make_salsah_link(x.attrib["id"]) for x in target_res])
    text_value = f"Start text{salsah_link}end text."  # type: ignore[possibly-undefined]
    return excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(text_value, encoding="xml"))


def _make_resptr_prop(target_id: list[str] | str, property_name: str = ":hasResource1") -> etree._Element:
    match target_id:
        case str():
            link = excel2xml.make_resptr_prop(name=property_name, value=target_id)
        # one resource with many targets
        case list():
            link = excel2xml.make_resptr_prop(name=property_name, value=target_id)
    return link  # type: ignore[possibly-undefined]


def _make_simple_text(resource: etree._Element) -> etree._Element:
    resource.append(excel2xml.make_text_prop(name=":hasSimpleText", value="This is text."))
    return resource


def _make_chain(replication_counter: str) -> list[etree._Element]:
    # A -> B -> C -> D -> E (resptr-prop)

    resources = _make_list_of_resources(5, replication_counter)
    resptr = [_make_resptr_prop(x.attrib["id"]) for x in resources[1:]]
    for i, link in enumerate(resptr):
        resources[i].append(link)
    return resources


def _make_one_circle_with_three_resources(replication_counter: str) -> list[etree._Element]:
    # A -> B (xml-text)
    # A -> B (resptr-prop)
    # B -> C (xml-text)
    # B -> C (resptr-prop)
    # C -> A (xml-text)
    # C -> A (resptr-prop)

    res_li = _make_list_of_resources(number_of_resources=3, replication_counter=replication_counter)
    salsah_list = [_make_xml_text_prop(x) for x in res_li]
    resptr_list = [_make_resptr_prop(x.attrib["id"]) for x in res_li]
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
    res_li[0].append(_make_resptr_prop(res_li[1].attrib["id"]))
    res_li[1].append(_make_xml_text_prop(res_li[0]))
    return res_li


def _make_complex_dependencies_single_link(replication_counter: str) -> list[etree._Element]:
    # A -> D (xml-text)
    # B -> D (xml-text)
    # C -> D (xml-text)
    # D -> E (resptr-prop)
    # E -> A (resptr-prop)
    # E -> B (resptr-prop)
    # E -> C (resptr-prop)

    all_resources = _make_list_of_resources(number_of_resources=5, replication_counter=replication_counter)
    all_resources = _make_complex_dependencies_single_link_resource_ABC(all_resources)
    all_resources = _make_complex_dependencies_single_link_resource_D(all_resources)
    return _make_complex_dependencies_single_link_resource_E(all_resources)


def _make_complex_dependencies_single_link_resource_ABC(resource_list: list[etree._Element]) -> list[etree._Element]:
    link_l = [_make_xml_text_prop(target_res=resource_list[3]) for _ in range(3)]
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_complex_dependencies_single_link_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(_make_resptr_prop(resource_list[4].attrib["id"]))
    return resource_list


def _make_complex_dependencies_single_link_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[4].append(_make_resptr_prop(target_id=[x.attrib["id"] for x in resource_list[:3]]))
    return resource_list


def _make_complex_dependencies_add_on(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies
    # plus
    # D -> F (xml-text)
    # F -> E (resptr-prop)

    complex_dep_li = _make_complex_dependencies_single_link(replication_counter)
    f_id = f"res_F_{replication_counter}"
    f_res: etree._Element = excel2xml.make_resource(restype=":TestThing", label=f_id, id=f_id)
    s_link = _make_xml_text_prop(target_res=f_res)
    f_res.append(_make_resptr_prop(complex_dep_li[-1].attrib["id"]))
    complex_dep_li[3].append(s_link)
    complex_dep_li.append(f_res)
    return complex_dep_li


def _make_complex_dependencies_with_simpletext(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies
    # plus each value has a simple text property

    complex_dep_li = _make_complex_dependencies_single_link(replication_counter)
    return [_make_simple_text(x) for x in complex_dep_li]


def _make_inverted_complex_dependencies(replication_counter: str) -> list[etree._Element]:
    # A -> D (resptr-prop)
    # B -> D (resptr-prop)
    # C -> D (resptr-prop)
    # D -> E (xml-text)
    # E -> A & B & C (xml-text) single <text> ele

    all_resources = _make_list_of_resources(number_of_resources=5, replication_counter=replication_counter)
    all_resources = _make_single_link_inverted_complex_dependencies_resource_ABC(all_resources)
    all_resources = _make_inverted_complex_dependencies_resource_D(all_resources)
    return _make_inverted_complex_dependencies_resource_E(all_resources)


def _make_single_link_inverted_complex_dependencies_resource_ABC(
    resource_list: list[etree._Element],
) -> list[etree._Element]:
    link_l = [_make_resptr_prop(target_id=resource_list[3].attrib["id"]) for _ in range(3)]
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_inverted_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(_make_xml_text_prop(resource_list[4]))
    return resource_list


def _make_inverted_complex_dependencies_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[4].append(_make_xml_text_prop(target_res=resource_list[:3]))
    return resource_list


def _make_complex_circular_dependencies_multi_link(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies_single_link
    # D -> E (resptr-prop) * 5
    all_resources = _make_list_of_resources(5, replication_counter)
    all_resources = _make_complex_dependencies_single_link_resource_ABC(all_resources)
    all_resources = _make_multi_link_complex_dependencies_resource_D(all_resources)
    return _make_complex_dependencies_single_link_resource_E(all_resources)


def _make_multi_link_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    target_resource = resource_list[4]
    links = [_make_resptr_prop(target_resource.attrib["id"], property_name=f":hasResource{n}") for n in range(1, 6)]
    resource_list[3].extend(links)
    return resource_list


def _make_multi_link_two_resource_circle(replication_counter: str) -> list[etree._Element]:
    # A -> B (resptr-prop) * 2
    # B -> A (xml-text)

    res_li = _make_list_of_resources(2, replication_counter)
    links = [_make_resptr_prop(res_li[1].attrib["id"], property_name=f":hasResource{n}") for n in range(1, 3)]
    res_li[0].extend(links)
    res_li[1].append(_make_xml_text_prop(res_li[0]))
    return res_li


def _make_two_resource_circle_plus_non_circle_link(replication_counter: str) -> list[etree._Element]:
    # A -> B (resptr-prop)
    # A -> C (resptr-prop)
    # B -> A (xml-text)

    all_resources = _make_list_of_resources(3, replication_counter)
    all_resources[0].append(_make_resptr_prop([x.attrib["id"] for x in all_resources[1:]]))
    all_resources[1].append(_make_xml_text_prop(all_resources[0]))
    return all_resources


def _make_single_text_ele_for_text_prop(target_resource_id: list[str]) -> etree._Element:
    salsa_links = [_make_salsah_link(x) for x in target_resource_id]
    text_values = [f"Start text{link}end text." for link in salsa_links]
    xml_props = [excel2xml.PropertyElement(text_value, encoding="xml") for text_value in text_values]
    return excel2xml.make_text_prop(name=":hasRichtext", value=xml_props)


def _make_three_resource_circle_with_multiple_text_prop(replication_counter: str) -> list[etree._Element]:
    # A -> B (resptr-prop)
    # A -> C (resptr-prop)
    # C -> A (xml-prop)
    # C -> B (xml-prop)

    all_resources = _make_list_of_resources(3, replication_counter)
    xml_links = _make_single_text_ele_for_text_prop([x.attrib["id"] for x in all_resources[:2]])
    all_resources[2].append(xml_links)
    resptr_links = _make_resptr_prop([x.attrib["id"] for x in all_resources[1:]])
    all_resources[0].append(resptr_links)
    return all_resources


def _make_three_resource_circle_multiple_diverse_links(replication_counter: str) -> list[etree._Element]:
    # A -> B (resptr-prop)
    # A -> B & C (xml-text) single <text> ele
    # A -> C (resptr-prop)
    # C -> A (xml-prop)
    # C -> B (xml-prop)

    resources = _make_three_resource_circle_with_multiple_text_prop(replication_counter)
    resources[0].append(_make_xml_text_prop(resources[1:]))
    return resources


def _make_complex_circle_with_leaf_nodes(replication_counter: str) -> list[etree._Element]:
    # Same as _make_complex_dependencies_add_on
    # plus
    # F ->
    resource_list = _make_complex_dependencies_add_on(replication_counter)
    leaf_resources = _make_list_of_resources(15, replication_counter, 75)
    xml_prop = _make_single_text_ele_for_text_prop([x.attrib["id"] for x in leaf_resources])
    resource_list[-1].append(xml_prop)
    resource_list.extend(leaf_resources)
    return resource_list


if __name__ == "__main__":
    create_and_save_circular_references_test_graph()
