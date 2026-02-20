"""
This module implements reading ontologies. ResourceClasses, PropertyClasses
as well as the assignment of PropertyCLasses to the ResourceClasses (with a given cardinality)
is handled in "cooperation" with the propertyclass.py (PropertyClass) and resourceclass.py (ResourceClass
and HasProperty) modules.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import regex

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.context import Context
from dsp_tools.commands.get.legacy_models.context import create_context
from dsp_tools.commands.get.legacy_models.helpers import get_json_ld_id
from dsp_tools.commands.get.legacy_models.propertyclass import PropertyClass
from dsp_tools.commands.get.legacy_models.propertyclass import create_property_class_from_json
from dsp_tools.commands.get.legacy_models.resourceclass import ResourceClass
from dsp_tools.commands.get.legacy_models.resourceclass import create_resource_class_from_json
from dsp_tools.error.exceptions import BaseError

# Module-level constants (previously class constants)
ONTOLOGY_ROUTE = "/v2/ontologies"
ONTOLOGY_METADATA = "/metadata/"
ALL_LANGUAGES = "?allLanguages=true"


@dataclass(frozen=True)
class Ontology:
    """Represents a DSP ontology with its resource and property classes."""

    iri: str
    name: str
    label: str
    comment: str | None
    resource_classes: tuple[ResourceClass, ...]
    property_classes: tuple[PropertyClass, ...]
    context: Context

    def to_definition_file_obj(self, con: Connection | None = None) -> dict[str, Any]:
        """Return a dictionary representation suitable for the definition file."""
        ontology: dict[str, Any] = {
            "name": self.name,
            "label": self.label,
            "comment": self.comment,
            "properties": [],
            "resources": [],
        }
        if not self.comment:
            ontology.pop("comment")

        skiplist: list[str] = []
        for prop in self.property_classes:
            if prop.superproperties and "knora-api:hasLinkToValue" in prop.superproperties:
                skiplist.append(self.name + ":" + prop.name)
                continue
            if con is not None:
                ontology["properties"].append(prop.to_definition_file_obj(con, self.context, self.name))

        for res in self.resource_classes:
            ontology["resources"].append(res.to_definition_file_obj(self.context, self.name, skiplist))

        return ontology


def _get_prefix(context: Context, iri: str) -> str:
    """Get prefix from context, raising an error if not found."""
    prefix = context.prefix_from_iri(iri)
    if prefix is None:
        raise BaseError(f"Could not resolve prefix for IRI: {iri}")
    return prefix


def create_ontology_from_json(json_obj: dict[str, Any], con: Connection | None = None) -> Ontology:
    """Create an Ontology from a JSON-LD object returned by the DSP API.

    The con parameter is kept for API compatibility but is not used in this function.
    """
    _ = con  # Mark as intentionally unused
    iri = json_obj.get("@id")
    if iri is None:
        raise BaseError("Ontology iri is missing")

    # evaluate the JSON-LD context to get the proper prefixes
    context = create_context(json_obj.get("@context"))
    onto_name = iri.split("/")[-2]
    context.add_context(onto_name, iri + "#")
    rdfs = _get_prefix(context, "http://www.w3.org/2000/01/rdf-schema#")
    knora_api = _get_prefix(context, "http://api.knora.org/ontology/knora-api/v2#")
    this_onto = _get_prefix(context, iri + "#")

    label = json_obj.get(rdfs + ":label")
    if label is None:
        raise BaseError("Ontology label is missing")
    comment = json_obj.get(rdfs + ":comment")
    if json_obj.get(knora_api + ":attachedToProject") is None:
        raise BaseError("Ontology not attached to a project")
    if json_obj[knora_api + ":attachedToProject"].get("@id") is None:
        raise BaseError("Ontology not attached to a project")

    resource_classes: tuple[ResourceClass, ...] = ()
    property_classes: tuple[PropertyClass, ...] = ()
    graph = json_obj.get("@graph")
    if graph is not None:
        resclasses_obj: list[dict[str, Any]] = list(
            filter(lambda a: a.get(knora_api + ":isResourceClass") is not None, graph)
        )
        resource_classes = tuple(create_resource_class_from_json(a) for a in resclasses_obj)

        properties_obj: list[dict[str, Any]] = list(
            filter(lambda a: a.get(knora_api + ":isResourceProperty") is not None, graph)
        )
        property_classes = tuple(
            create_property_class_from_json(a)
            for a in properties_obj
            if get_json_ld_id(a.get(knora_api + ":objectType")) != "knora-api:LinkValue"
        )

    return Ontology(
        iri=iri,
        name=this_onto,
        label=label,
        comment=comment,
        resource_classes=resource_classes,
        property_classes=property_classes,
        context=context,
    )


def _create_one_ontology_from_metadata(json_obj: dict[str, Any], context: Context) -> Ontology | None:
    """Create an Ontology from a metadata JSON object (used when listing all ontologies)."""
    rdfs = _get_prefix(context, "http://www.w3.org/2000/01/rdf-schema#")
    owl = _get_prefix(context, "http://www.w3.org/2002/07/owl#")
    knora_api = _get_prefix(context, "http://api.knora.org/ontology/knora-api/v2#")

    if json_obj.get("@type") != owl + ":Ontology":
        return None

    iri = json_obj.get("@id")
    if iri is None:
        raise BaseError("Ontology iri is missing")
    if json_obj.get(knora_api + ":attachedToProject") is None:
        raise BaseError("Ontology not attached to a project (1)")
    if json_obj[knora_api + ":attachedToProject"].get("@id") is None:
        raise BaseError("Ontology not attached to a project (2)")

    label = json_obj.get(rdfs + ":label")
    if label is None:
        raise BaseError("Ontology label is missing")
    comment = json_obj.get(rdfs + ":comment")
    this_onto = iri.split("/")[-2]

    context2 = copy.deepcopy(context)
    context2.add_context(this_onto, iri)

    return Ontology(
        iri=iri,
        name=this_onto,
        label=label,
        comment=comment,
        resource_classes=(),
        property_classes=(),
        context=context2,
    )


def create_all_ontologies_from_json(json_obj: dict[str, Any]) -> list[Ontology]:
    """Create a list of Ontology objects from a JSON response containing multiple ontologies."""
    context = create_context(json_obj.get("@context"))
    ontos: list[Ontology] = []
    if json_obj.get("@graph") is not None:
        for o in json_obj["@graph"]:
            onto = _create_one_ontology_from_metadata(o, context)
            if onto is not None:
                ontos.append(onto)
    else:
        onto = _create_one_ontology_from_metadata(json_obj, context)
        if onto is not None:
            ontos.append(onto)
    return ontos


def get_project_ontologies(con: Connection, project_id: str) -> list[Ontology]:
    """Get all ontologies for a project from the DSP server."""
    result = con.get(ONTOLOGY_ROUTE + ONTOLOGY_METADATA + quote_plus(project_id) + ALL_LANGUAGES)
    return create_all_ontologies_from_json(result)


def get_ontology_from_server(con: Connection, shortcode: str, name: str) -> Ontology:
    """Get a specific ontology from the DSP server."""
    if regex.search(r"[0-9A-F]{4}", shortcode):
        result = con.get("/ontology/" + shortcode + "/" + name + "/v2" + ALL_LANGUAGES)
    else:
        result = con.get("/ontology/" + name + "/v2" + ALL_LANGUAGES)
    return create_ontology_from_json(result)
