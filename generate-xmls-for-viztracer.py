from enum import Enum

from lxml import etree

from dsp_tools.excel2xml import PropertyElement, make_root, make_resource, make_resptr_prop, make_text_prop, write_xml


class __Letter(Enum):
    A = 0
    B = 1
    C = 2


def __make_circle(resource_counter: int) -> list[etree._Element]:
    return [__make_one_resource(resource_counter=resource_counter, letter=x) for x in __Letter]


def __make_one_resource(resource_counter: int, letter: __Letter) -> etree._Element:
    id_1 = f"resource_{resource_counter}_{letter.name}"
    id_2 = f"resource_{resource_counter}_{__Letter((letter.value + 1) % len(__Letter)).name}"
    salsah_link = f'<a class="salsah-link" href="IRI:{id_2}:IRI">{id_2}</a>'
    resource = make_resource(restype=":TestThing", label=id_1, id=id_1)
    resource.append(make_resptr_prop(name=":hasResource", value=id_2))
    resource.append(make_text_prop(name=":hasRichtext", value=PropertyElement(salsah_link, encoding="xml")))
    return resource


def __generate_xmls_for_viztracer() -> None:
    number_of_circles = 10
    root = make_root("4123", "testonto")
    for i in range(1, number_of_circles + 1):
        root.extend(__make_circle(resource_counter=i))
    write_xml(root, f"circles-{number_of_circles}.xml")


if __name__ == "__main__":
    __generate_xmls_for_viztracer()
