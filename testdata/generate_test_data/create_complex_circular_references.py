import os.path
from typing import Any

from lxml import etree

from dsp_tools import excel2xml


def create_and_save_circular_references_test_graph(number_of_graphs: int, save_location: str = "") -> None:
    root = create_circular_references_test_graph(replication_counter=number_of_graphs)
    excel2xml.write_xml(root, os.path.join(save_location, f"test_circular_references_{number_of_graphs}.xml"))


def create_circular_references_test_graph(replication_counter: int) -> etree._Element:
    root = excel2xml.make_root("4123", "testonto")
    for i in range(1, replication_counter + 1):
        root.extend(_make_one_circle_with_three_resources(replication_counter=f"{i}1"))
        root.extend(_make_complex_dependencies(replication_counter=f"{i}2"))
        root.extend(_make_complex_dependencies_add_on(replication_counter=f"{i}3"))
        root.extend(_make_two_references(replication_counter=f"{i}4"))
        root.append(_make_reflexive_reference(replication_counter=f"{i}5"))
    return root


def _make_list_of_resources(number_of_resources: int, replication_counter: str, start_range: int = 65) -> list[Any]:
    letters = [chr(x) for x in range(start_range, start_range + number_of_resources)]
    return [
        excel2xml.make_resource(
            restype=":TestThing", label=f"res_{let}_{replication_counter}", id=f"res_{let}_{replication_counter}"
        )
        for let in letters
    ]


def _make_salsah_link_prop(target_res: etree._Element) -> etree._Element:
    salsah_link = f'<a class="salsah-link" href="IRI:{target_res.attrib["id"]}:IRI">{target_res.attrib["id"]}</a>'
    return excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))


def _make_resptr_prop(target_res: list[etree._Element]) -> etree._Element:
    return excel2xml.make_resptr_prop(name=":hasResource", value=[x.attrib["id"] for x in target_res])


def _make_complex_dependencies_add_on(replication_counter: str) -> list[etree._Element]:
    """
    Same as _make_complex_dependencies
    plus
    D -> F (resptr-prop)
    """
    complex_dep_li = _make_complex_dependencies(replication_counter)
    f_id = f"res_F_{replication_counter}"
    f_res: etree._Element = excel2xml.make_resource(restype=":TestThing", label=f_id, id=f_id)
    s_link = _make_salsah_link_prop(target_res=f_res)
    complex_dep_li[3].append(s_link)
    complex_dep_li.append(f_res)
    return complex_dep_li


def _make_complex_dependencies(replication_counter: str) -> list[etree._Element]:
    """
    A -> D (salsah-link)
    B -> D (salsah-link)
    C -> D (salsah-link)
    D -> E (resptr-prop)
    E -> A / B / C (resptr-prop)
    """
    all_resources = _make_list_of_resources(number_of_resources=5, replication_counter=replication_counter)
    all_resources = _make_complex_dependencies_resource_ABC(all_resources)
    all_resources = _make_complex_dependencies_resource_D(all_resources)
    return _make_complex_dependencies_resource_E(all_resources)


def _make_complex_dependencies_resource_ABC(resource_list: list[etree._Element]) -> list[etree._Element]:
    link_l = [_make_salsah_link_prop(target_res=resource_list[3]) for i in range(3)]
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(excel2xml.make_resptr_prop(name=":hasResource", value=resource_list[4].attrib["id"]))
    return resource_list


def _make_complex_dependencies_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[4].append(_make_resptr_prop(target_res=resource_list[0:2]))
    resource_list[4].append(_make_salsah_link_prop(target_res=resource_list[2]))
    return resource_list


def _make_one_circle_with_three_resources(replication_counter: str) -> list[etree._Element]:
    """
    A -> B (salsah-link) & (resptr-prop)
    B -> C (salsah-link) & (resptr-prop)
    C -> A (salsah-link) & (resptr-prop)
    """
    res_li = _make_list_of_resources(number_of_resources=3, replication_counter=replication_counter)
    salsah_list = [_make_salsah_link_prop(x) for x in res_li]
    resptr_list = [_make_resptr_prop([x]) for x in res_li]
    res_li[0].append(salsah_list[1])
    res_li[0].append(resptr_list[1])
    res_li[1].append(salsah_list[2])
    res_li[1].append(resptr_list[2])
    res_li[2].append(salsah_list[0])
    res_li[2].append(resptr_list[0])
    return res_li


def _make_two_references(replication_counter: str) -> list[etree._Element]:
    """
    A -> B (resptr-prop)
    B -> A (salsah-link)
    """
    res_li = _make_list_of_resources(2, replication_counter)
    res_li[0].append(_make_resptr_prop([res_li[1]]))
    res_li[1].append(_make_salsah_link_prop(res_li[0]))
    return res_li


def _make_reflexive_reference(replication_counter: str) -> Any:
    """
    A -> A
    """
    res = _make_list_of_resources(1, replication_counter)[0]
    res.append(_make_resptr_prop([res]))
    return res
