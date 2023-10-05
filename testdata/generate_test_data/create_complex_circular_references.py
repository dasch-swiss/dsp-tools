import os.path
from enum import Enum
from pathlib import Path
from typing import Any

from lxml import etree

from dsp_tools import excel2xml


class _Letter(Enum):
    A = 0
    B = 1
    C = 2


def create_and_save_circular_references_test_graph(graph_num: int, save_location: str = "") -> None:
    root = create_circular_references_test_graph(replication_counter=graph_num)
    excel2xml.write_xml(root, os.path.join(save_location, f"test_circular_references_{graph_num}.xml"))


def create_circular_references_test_graph(replication_counter: int) -> etree._ElementTree:
    root = excel2xml.make_root("4123", "testonto")
    for i in range(1, replication_counter + 1):
        root.extend(_make_circle_list(resource_counter=f"{i}1"))
        root.extend(_make_complex_dependencies(graph_number=f"{i}2"))
        root.extend(_make_complex_dependencies_add_on(graph_number=f"{i}3"))
    return root


def _make_complex_dependencies_add_on(graph_number: str) -> list[etree._Element]:
    """
    Same as _make_complex_dependencies
    plus
    D -> F (resptr-prop)
    """
    complex_dep_li = _make_complex_dependencies(graph_number)
    f_id = f"res_F_{graph_number}"
    f: etree._Element = excel2xml.make_resource(restype=":TestThing", label=f_id, id=f_id)
    salsah_link = f'<a class="salsah-link" href="IRI:{f_id}:IRI">{f_id}</a>'
    s_link = excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))
    complex_dep_li[3].append(s_link)
    complex_dep_li.append(f)
    return complex_dep_li


def _make_complex_dependencies(graph_number: str) -> list[etree._Element]:
    """
    A -> D (salsah-link)
    B -> D (salsah-link)
    C -> D (salsah-link)
    D -> E (resptr-prop)
    E -> A / B / C (resptr-prop)
    """
    all_resources = _make_list_of_resources(number_of_resources=5, graph_number=graph_number)
    all_resources = _make_complex_dependencies_resource_ABC(all_resources)
    all_resources = _make_complex_dependencies_resource_D(all_resources)
    return _make_complex_dependencies_resource_E(all_resources)


def _make_circle_list(resource_counter: str) -> list[etree._Element]:
    """
    A -> B (salsah-link)
    B -> C (resptr-prop)
    C -> A (resptr-prop)
    C -> A (salsah-link)
    """
    return [_make_one_circle_with_three_resources(resource_counter=resource_counter, letter=x) for x in _Letter]


def _get_letter_list(number_of_letters: int, start_range: int = 65) -> list[str]:
    return [chr(x) for x in range(start_range, start_range + number_of_letters)]


def _make_list_of_resources(number_of_resources: int, graph_number: str) -> list[Any]:
    letters = _get_letter_list(number_of_resources)
    return [
        excel2xml.make_resource(restype=":TestThing", label=f"res_{let}_{graph_number}", id=f"res_{let}_{graph_number}")
        for let in letters
    ]


def _make_complex_dependencies_resource_D(resource_list: list[etree._Element]) -> list[etree._Element]:
    resource_list[3].append(excel2xml.make_resptr_prop(name=":hasResource", value=resource_list[4].attrib["id"]))
    return resource_list


def _make_complex_dependencies_resource_E(resource_list: list[etree._Element]) -> list[etree._Element]:
    r_id = resource_list[2].attrib["id"]
    salsah_link = f'<a class="salsah-link" href="IRI:{r_id}:IRI">{r_id}</a>'
    v = [x.attrib["id"] for x in resource_list[0:2]]
    resource_list[4].append(
        excel2xml.make_resptr_prop(name=":hasResource", value=[x.attrib["id"] for x in resource_list[0:2]])
    )
    resource_list[4].append(
        excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))
    )
    return resource_list


def _make_complex_dependencies_resource_ABC(resource_list: list[etree._Element]) -> list[etree._Element]:
    link_l = _make_salsah_link_list(3, resource_list[3])
    for i in range(3):
        resource_list[i].append(link_l[i])
    return resource_list


def _make_salsah_link_list(list_len: int, target_res: etree._Element) -> list[etree._Element]:
    r_id = target_res.attrib["id"]
    salsah_link = f'<a class="salsah-link" href="IRI:{r_id}:IRI">{r_id}</a>'
    return [
        excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))
        for x in range(list_len)
    ]


def _make_one_circle_with_three_resources(resource_counter: str, letter: _Letter) -> etree._Element:
    id_1 = f"resource_{resource_counter}_{letter.name}"
    id_2 = f"resource_{resource_counter}_{_Letter((letter.value + 1) % len(_Letter)).name}"
    salsah_link = f'<a class="salsah-link" href="IRI:{id_2}:IRI">{id_2}</a>'
    resource = excel2xml.make_resource(restype=":TestThing", label=id_1, id=id_1)
    resource.append(excel2xml.make_resptr_prop(name=":hasResource", value=id_2))
    resource.append(
        excel2xml.make_text_prop(name=":hasRichtext", value=excel2xml.PropertyElement(salsah_link, encoding="xml"))
    )
    resource.append(excel2xml.make_text_prop(":hasSimpleText", "foo"))
    resource.append(excel2xml.make_boolean_prop(":hasBoolean", "True"))
    return resource
