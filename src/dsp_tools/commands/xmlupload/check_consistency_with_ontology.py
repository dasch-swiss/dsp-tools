from datetime import datetime
from pathlib import Path
from typing import cast

import regex
from lxml import etree
from regex import Pattern

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import AllowedEncodings
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import ProjectOntosInformation
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import PropertyTextValueTypes
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import TextValueData
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import get_text_value_types_of_properties_from_onto
from dsp_tools.commands.xmlupload.models.ontology_lookup_models import make_project_onto_information
from dsp_tools.commands.xmlupload.models.ontology_problem_models import InvalidOntologyElementsInData
from dsp_tools.commands.xmlupload.models.ontology_problem_models import InvalidTextValueEncodings
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient
from dsp_tools.models.exceptions import InputError

defaultOntologyColon: Pattern[str] = regex.compile(r"^:\w+$")
knoraUndeclared: Pattern[str] = regex.compile(r"^\w+$")
genericPrefixedOntology: Pattern[str] = regex.compile(r"^[\w\-]+:\w+$")


def do_xml_consistency_check_with_ontology(onto_client: OntologyClient, root: etree._Element) -> None:
    """
    This function takes an OntologyClient and the root of an XML.
    It retrieves the ontologies from the server.
    It analyses if any classes or properties are used that are not in the ontology.
    It analyses if any properties have encodings that are not consistent with those specified in the ontology.

     Args:
         onto_client: client for the ontology retrieval
         root: root of the XML

     Raises:
         InputError: if there are any invalid properties or classes and/or text values with wrong encodings.
    """
    cls_prop_lookup, text_value_encoding_lookup = _get_onto_lookups(onto_client)
    classes_in_data, properties_in_data = _get_all_classes_and_properties_from_data(root)
    problem_str = ""
    problem_str += _check_all_classes_and_properties_in_onto(classes_in_data, properties_in_data, cls_prop_lookup)
    problem_str += _check_correctness_all_text_value_encodings(root, text_value_encoding_lookup)
    if problem_str:
        raise InputError(problem_str)


def _get_onto_lookups(onto_client: OntologyClient) -> tuple[ProjectOntosInformation, PropertyTextValueTypes]:
    ontos = onto_client.get_all_project_ontologies_from_server()
    text_value_encoding_lookup = get_text_value_types_of_properties_from_onto(ontos, onto_client.default_ontology)
    ontos["knora-api"] = onto_client.get_knora_api_ontology_from_server()
    return make_project_onto_information(onto_client.default_ontology, ontos), text_value_encoding_lookup


def _check_all_classes_and_properties_in_onto(
    classes_in_data: dict[str, list[str]],
    properties_in_data: dict[str, list[str]],
    onto_check_info: ProjectOntosInformation,
) -> str:
    class_problems = _find_all_class_types_in_onto(classes_in_data, onto_check_info)
    property_problems = _find_all_properties_in_onto(properties_in_data, onto_check_info)
    if not class_problems and not property_problems:
        return ""
    problems = InvalidOntologyElementsInData(
        classes=class_problems, properties=property_problems, ontos_on_server=list(onto_check_info.onto_lookup.keys())
    )
    msg, df = problems.execute_problem_protocol()
    if df is not None:
        csv_file = f"XML_syntax_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
        df.to_csv(path_or_buf=Path(Path.cwd(), csv_file), index=False)
        msg += (
            "\n\n---------------------------------------\n\n"
            f"\nAll the problems are listed in the file: '{Path.cwd()}/{csv_file}'\n"
        )
    return msg


def _get_all_classes_and_properties_from_data(
    root: etree._Element,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    cls_dict = _get_all_class_types_and_ids_from_data(root)
    prop_dict: dict[str, list[str]] = {}
    for resource in root.iterchildren(tag="resource"):
        prop_dict = _get_all_property_names_and_resource_ids_one_resource(resource, prop_dict)
    return cls_dict, prop_dict


def _get_all_class_types_and_ids_from_data(root: etree._Element) -> dict[str, list[str]]:
    cls_dict: dict[str, list[str]] = {}
    for resource in root.iterchildren(tag="resource"):
        restype = resource.attrib["restype"]
        if restype in cls_dict:
            cls_dict[restype].append(resource.attrib["id"])
        else:
            cls_dict[restype] = [resource.attrib["id"]]
    return cls_dict


def _get_all_property_names_and_resource_ids_one_resource(
    resource: etree._Element, prop_dict: dict[str, list[str]]
) -> dict[str, list[str]]:
    for prop in resource.iterchildren():
        if prop.tag != "bitstream":
            prop_name = prop.attrib["name"]
            if prop_name in prop_dict:
                prop_dict[prop_name].append(resource.attrib["id"])
            else:
                prop_dict[prop_name] = [resource.attrib["id"]]
    return prop_dict


def _find_all_class_types_in_onto(
    classes: dict[str, list[str]], onto_check_info: ProjectOntosInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for cls_type, ids in classes.items():
        if problem := _find_one_class_type_in_onto(cls_type, onto_check_info):
            problem_list.append((cls_type, ids, problem))
    return problem_list


def _find_one_class_type_in_onto(cls_type: str, onto_check_info: ProjectOntosInformation) -> str | None:
    prefix, cls_ = _get_separate_prefix_and_iri_from_onto_prop_or_cls(cls_type, onto_check_info.default_ontology_prefix)
    if not prefix:
        return "Class name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Class Type" if cls_ not in onto.classes else None
    else:
        return "Unknown ontology prefix"


def _find_all_properties_in_onto(
    properties: dict[str, list[str]], onto_check_info: ProjectOntosInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for prop_name, ids in properties.items():
        if problem := _find_one_property_in_onto(prop_name, onto_check_info):
            problem_list.append((prop_name, ids, problem))
    return problem_list


def _find_one_property_in_onto(prop_name: str, onto_check_info: ProjectOntosInformation) -> str | None:
    prefix, prop = _get_separate_prefix_and_iri_from_onto_prop_or_cls(
        prop_name, onto_check_info.default_ontology_prefix
    )
    if not prefix:
        return "Property name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Property" if prop not in onto.properties else None
    else:
        return "Unknown ontology prefix"


def _get_separate_prefix_and_iri_from_onto_prop_or_cls(
    prop_or_cls: str, default_ontology_prefix: str
) -> tuple[str, ...] | tuple[None, None]:
    if defaultOntologyColon.match(prop_or_cls):
        return default_ontology_prefix, prop_or_cls.lstrip(":")
    elif knoraUndeclared.match(prop_or_cls):
        return "knora-api", prop_or_cls
    elif genericPrefixedOntology.match(prop_or_cls):
        return tuple(prop_or_cls.split(":"))
    else:
        return None, None


def _check_correctness_all_text_value_encodings(root: etree._Element, text_prop_look_up: PropertyTextValueTypes) -> str:
    """
    This function analyses if all the encodings for the <text> elements are correct
    with respect to the specification in the ontology.

    For example, if the ontology specifies that `:hasSimpleText` is without mark-up,
    the encoding has to be `utf8`.


    This is correct:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Dies ist ein einfacher Text ohne Markup</text>
    </text-prop>
    ```

    This is wrong:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="xml">Dies ist ein einfacher Text ohne Markup</text>
    </text-prop>
    ```

    The accepted encodings are `xml` or `utf8`

    Args:
        root: root of the data xml document
        text_prop_look_up: a lookup containing the property names and their specified types

    Returns:
        A string communicating the problem, if there are none the string is empty.
    """
    text_values_in_data = _get_all_ids_and_props_and_encodings_from_root(root)
    invalid_text_values = [x for x in text_values_in_data if not _check_correctness_of_one_prop(x, text_prop_look_up)]
    if len(invalid_text_values) == 0:
        return ""
    msg, df = InvalidTextValueEncodings(invalid_text_values).execute_problem_protocol()
    if df is not None:
        csv_file = Path(f"text_value_encoding_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv")
        df.to_csv(path_or_buf=csv_file, index=False)
        msg += (
            "\n\n---------------------------------------\n\n"
            f"All the problems are listed in the file: '{csv_file.absolute()}'"
        )
    return msg


def _get_all_ids_and_props_and_encodings_from_root(root: etree._Element) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        res_list.extend(_get_id_and_props_and_encodings_from_one_resource(res_input))
    return res_list


def _get_id_and_props_and_encodings_from_one_resource(resource: etree._Element) -> list[TextValueData]:
    res_id = resource.attrib["id"]
    return [_get_prop_and_encoding_from_one_property(res_id, child) for child in resource.iterchildren(tag="text-prop")]


def _get_prop_and_encoding_from_one_property(res_id: str, property: etree._Element) -> TextValueData:
    prop_name = property.attrib["name"]
    encoding = cast(AllowedEncodings, property[0].attrib["encoding"])
    return TextValueData(res_id, prop_name, encoding)


def _check_correctness_of_one_prop(text_val: TextValueData, text_prop_look_up: PropertyTextValueTypes) -> bool:
    match text_val.encoding:
        case "xml":
            return text_val.property_name in text_prop_look_up.formatted_text_props
        case "utf8":
            return text_val.property_name in text_prop_look_up.unformatted_text_props
        case _:
            return False
