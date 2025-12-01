from typing import Any
from typing import cast

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parsing_utils import resolve_to_absolute_iri

CARDINALITY_MAPPER = {
    "0-1": Cardinality.C_0_1,
    "1": Cardinality.C_1,
    "0-n": Cardinality.C_0_N,
    "1-n": Cardinality.C_1_N,
}

OBJECT_TYPE_MAPPER = {
    "BooleanValue": KnoraObjectType.BOOLEAN,
    "ColorValue": KnoraObjectType.COLOR,
    "DateValue": KnoraObjectType.DATE,
    "DecimalValue": KnoraObjectType.DECIMAL,
    "GeonameValue": KnoraObjectType.GEONAME,
    "IntValue": KnoraObjectType.INT,
    "ListValue": KnoraObjectType.LIST,
    "TextValue": KnoraObjectType.TEXT,
    "TimeValue": KnoraObjectType.TIME,
    "UriValue": KnoraObjectType.URI,
}

GUI_ELEMENT_MAPPER = {
    "Checkbox": GuiElement.CHECKBOX,
    "Colorpicker": GuiElement.COLORPICKER,
    "Date": GuiElement.DATE,
    "Spinbox": GuiElement.SPINBOX,
    "Geonames": GuiElement.GEONAMES,
    "List": GuiElement.LIST,
    "SimpleText": GuiElement.SIMPLETEXT,
    "Textarea": GuiElement.TEXTAREA,
    "Richtext": GuiElement.RICHTEXT,
    "Searchbox": GuiElement.SEARCHBOX,
    "TimeStamp": GuiElement.TIME_STAMP,
}


def parse_ontology(ontology_json: dict[str, Any], prefixes: dict[str, str]) -> ParsedOntology | CollectedProblems:
    onto_name = ontology_json["name"]
    current_onto = prefixes[onto_name]
    fails = []
    props, prop_fails = _parse_properties(ontology_json["properties"], current_onto, prefixes)
    fails.extend(prop_fails)
    classes, cls_fails = _parse_classes(ontology_json["resources"], current_onto, prefixes)
    fails.extend(cls_fails)
    cards, card_fails = _parse_cardinalities(ontology_json["resources"], current_onto, prefixes)
    fails.extend(card_fails)
    if fails:
        return CollectedProblems(
            f"During the parsing of the ontology '{onto_name}' the following errors occurred", fails
        )
    return ParsedOntology(
        name=onto_name,
        label=ontology_json["label"],
        comment=ontology_json.get("comment"),
        classes=classes,
        properties=props,
        cardinalities=cards,
    )


def _parse_properties(
    properties_list: list[dict[str, Any]],
    current_onto_prefix: str,
    prefixes: dict[str, str],
) -> tuple[list[ParsedProperty], list[CreateProblem]]:
    problems: list[CreateProblem] = []
    parsed = []
    for prop in properties_list:
        result = _parse_one_property(prop, current_onto_prefix, prefixes)
        if isinstance(result, ParsedProperty):
            parsed.append(result)
        else:
            problems.extend(result)
    return parsed, problems


def _parse_one_property(
    prop: dict[str, Any], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedProperty | list[CreateProblem]:
    problems: list[CreateProblem] = []
    prop_name = f"{current_onto_prefix}{prop['name']}"
    labels = prop["labels"]
    comments = prop.get("comments")
    object_str = prop["object"]
    gui_element = GUI_ELEMENT_MAPPER[prop["gui_element"]]
    subject = prop.get("subject")

    supers = []
    for super_prop in prop["super"]:
        if not (resolved := resolve_to_absolute_iri(super_prop, current_onto_prefix, prefixes)):
            problems.append(
                InputProblem(
                    f'At property "{prop["name"]}" / Super: "{super_prop}"',
                    InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
        else:
            supers.append(resolved)

    if gui_element == GuiElement.SEARCHBOX:
        if not (obj_iri := resolve_to_absolute_iri(object_str, current_onto_prefix, prefixes)):
            problems.append(
                InputProblem(
                    f'At property "{prop["name"]}" / Object: "{object_str}"',
                    InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
            object_value = ""
        else:
            object_value = obj_iri
    else:
        object_value = OBJECT_TYPE_MAPPER[object_str]

    if subject:
        if not (resolved_subject := resolve_to_absolute_iri(prop["subject"], current_onto_prefix, prefixes)):
            problems.append(
                InputProblem(
                    f'At property "{prop["name"]}" / Subject: "{subject}"',
                    InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
        subject = resolved_subject

    list_name = None
    if object_value == KnoraObjectType.LIST:
        list_name = prop["gui_attributes"]["hlist"]

    if problems:
        return problems
    return ParsedProperty(
        name=prop_name,
        labels=labels,
        comments=comments,
        supers=supers,
        object=object_value,
        subject=subject,
        gui_element=gui_element,
        node_name=list_name,
        onto_iri=current_onto_prefix.rstrip("#"),
    )


def _parse_classes(
    classes_list: list[dict[str, Any]], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedClass], list[CreateProblem]]:
    parsed = []
    problems = []
    for cls in classes_list:
        result = _parse_one_class(cls, current_onto_prefix, prefixes)
        if isinstance(result, ParsedClass):
            parsed.append(result)
        else:
            problems.extend(result)
    return parsed, problems


def _parse_one_class(
    cls: dict[str, Any], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedClass | list[CreateProblem]:
    problems: list[CreateProblem] = []
    supers = [cls["super"]] if isinstance(cls["super"], str) else cls["super"]
    resolved_supers = []
    for s in supers:
        if not (resolved_super := resolve_to_absolute_iri(s, current_onto_prefix, prefixes)):
            problems.append(
                InputProblem(
                    f'At class "{cls["name"]}" / Super: "{s}"',
                    InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
        else:
            resolved_supers.append(resolved_super)
    if problems:
        return problems
    return ParsedClass(
        name=f"{current_onto_prefix}{cls['name']}",
        labels=cls["labels"],
        comments=cls.get("comments"),
        supers=resolved_supers,
        onto_iri=current_onto_prefix.rstrip("#"),
    )


def _parse_cardinalities(
    classes_list: list[dict[str, Any]], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedClassCardinalities], list[CreateProblem]]:
    parsed = []
    failures = []
    for c in classes_list:
        if c.get("cardinalities"):
            result = _parse_one_class_cardinality(c, current_onto_prefix, prefixes)
            if isinstance(result, ParsedClassCardinalities):
                parsed.append(result)
            else:
                failures.extend(result)
    return parsed, failures


def _parse_one_class_cardinality(
    cls_json: dict[str, Any], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedClassCardinalities | list[CreateProblem]:
    failures = []
    parsed = []
    for c in cls_json["cardinalities"]:
        result = _parse_one_cardinality(c, current_onto_prefix, prefixes)
        if isinstance(result, ParsedPropertyCardinality):
            parsed.append(result)
        else:
            failures.append(result)
    if failures:
        return failures
    cls_iri = f"{current_onto_prefix}{cls_json['name']}"
    return ParsedClassCardinalities(cls_iri, parsed)


def _parse_one_cardinality(
    card_json: dict[str, str | int], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedPropertyCardinality | CreateProblem:
    prp_name = cast(str, card_json["propname"])
    if not (resolved := resolve_to_absolute_iri(prp_name, current_onto_prefix, prefixes)):
        return CreateProblem(prp_name, InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED)
    gui = cast(int | None, card_json.get("gui_order"))
    return ParsedPropertyCardinality(
        propname=resolved,
        cardinality=CARDINALITY_MAPPER[cast(str, card_json["cardinality"])],
        gui_order=gui,
    )
