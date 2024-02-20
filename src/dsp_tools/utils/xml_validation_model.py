from dataclasses import dataclass

from lxml import etree


@dataclass
class TextValueData:
    resource_id: str
    property_name: str
    encoding: set[str]


def _get_all_ids_prop_encoding_from_root(root: etree._Element) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        if (res_result := _get_id_prop_encoding_from_one_resource(res_input)) is not None:
            res_list.extend(res_result)
    return res_list


def _get_id_prop_encoding_from_one_resource(resource: etree._Element) -> list[TextValueData] | None:
    if not (children := list(resource.iterchildren(tag="text-prop"))):
        return None
    res_id = resource.attrib["id"]
    return [_get_prop_encoding_from_one_property(res_id, child) for child in children]


def _get_prop_encoding_from_one_property(res_id: str, property: etree._Element) -> TextValueData:
    prop_name = property.attrib["name"]
    child_attrib = [x.attrib for x in property.iterchildren()]
    encodings = {x["encoding"] for x in child_attrib}
    return TextValueData(res_id, prop_name, encodings)


def _check_only_one_valid_encoding_used_all_props(text_props: list[TextValueData]) -> list[TextValueData] | None:
    wrong_props = [x for x in text_props if not _check_only_one_valid_encoding_used_one_prop(x.encoding)]
    if len(wrong_props) == 0:
        return None
    return wrong_props


def _check_only_one_valid_encoding_used_one_prop(text_encodings: set[str]) -> bool:
    if text_encodings == {"xml"} or text_encodings == {"utf8"}:  # noqa: PLR1714
        return True
    return False
