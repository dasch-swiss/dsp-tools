"""
This module implements reading resource classes. It contains two classes that work closely together:
    * "HasProperty" deals with the association of Property-instances with the Resource-instances. This association
      is done using the "cardinality"-clause
    * "ResourceClass" is the main class representing a DSP resource class.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from dsp_tools.commands.get.legacy_models.context import Context
from dsp_tools.commands.get.legacy_models.helpers import Cardinality
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json_ld


class Ptype(Enum):
    """Property type classification."""

    system = 1
    knora = 2
    other = 3


@dataclass(frozen=True)
class HasProperty:
    """Represents a property assignment to a resource class with cardinality."""

    property_id: str
    cardinality: Cardinality
    ptype: Ptype
    gui_order: int | None

    def to_definition_file_obj(self, context: Context, shortname: str) -> dict[str, Any]:
        """Create an object for the definition file export."""
        cardinality_obj: dict[str, Any] = {}
        if self.ptype == Ptype.other or self.property_id in [
            "knora-api:isPartOf",
            "knora-api:seqnum",
        ]:
            cardinality_obj["propname"] = context.reduce_iri(self.property_id, shortname)
            cardinality_obj["cardinality"] = self.cardinality.value
            if self.gui_order is not None:
                cardinality_obj["gui_order"] = self.gui_order
        return cardinality_obj


def create_has_property_from_json(jsonld_obj: dict[str, Any]) -> tuple[str, HasProperty]:
    """
    Create a HasProperty from a JSON-LD object.

    Args:
        jsonld_obj: JSON-LD object from DSP API

    Returns:
        Tuple of (property_id, HasProperty instance)
    """
    if jsonld_obj.get("@type") != "owl:Restriction":
        raise BaseError("Expected restriction type")

    cardinality = _extract_cardinality(jsonld_obj)
    property_id, ptype = _extract_property_type_iri(jsonld_obj)

    gui_order: int | None = jsonld_obj.get("salsah-gui:guiOrder")

    return property_id, HasProperty(
        property_id=property_id,
        cardinality=cardinality,
        ptype=ptype,
        gui_order=gui_order,
    )


def _extract_property_type_iri(jsonld_obj: dict[str, Any]) -> tuple[str, Ptype]:
    """Extract property IRI and determine its type."""
    on_property = jsonld_obj.get("owl:onProperty")
    if on_property is None:
        raise BaseError("No property IRI given")
    property_id = on_property.get("@id")
    if property_id is None:
        raise BaseError("No property IRI given")
    prefix = property_id.split(":")[0]
    if prefix in ("rdf", "rdfs", "owl"):
        ptype = Ptype.system
    elif prefix == "knora-api":
        ptype = Ptype.knora
    else:
        ptype = Ptype.other
    return property_id, ptype


def _extract_cardinality(jsonld_obj: dict[str, Any]) -> Cardinality:
    """Extract cardinality from JSON-LD object."""
    if jsonld_obj.get("owl:cardinality") is not None:
        return Cardinality.C_1
    elif jsonld_obj.get("owl:maxCardinality") is not None:
        return Cardinality.C_0_1
    elif jsonld_obj.get("owl:minCardinality") is not None:
        if jsonld_obj.get("owl:minCardinality") == 0:
            return Cardinality.C_0_n
        elif jsonld_obj.get("owl:minCardinality") == 1:
            return Cardinality.C_1_n
        else:
            raise BaseError("Problem with cardinality")
    else:
        raise BaseError("Problem with cardinality")


@dataclass(frozen=True)
class ResourceClass:
    """Represents a DSP resource class definition."""

    name: str
    superclasses: tuple[str, ...] | None
    label: LangString
    comment: LangString
    has_properties: dict[str, HasProperty] | None

    def to_definition_file_obj(self, context: Context, shortname: str, skiplist: list[str]) -> dict[str, Any]:
        """Create an object for the definition file export."""
        resource: dict[str, Any] = {"name": self.name}
        if self.superclasses:
            resource["super"] = _build_superclass_obj(context, shortname, self.superclasses)
        resource["labels"] = self.label.to_definition_file_obj()
        if not self.comment.is_empty():
            resource["comments"] = self.comment.to_definition_file_obj()
        if self.has_properties:
            _add_cardinalities(context, resource, shortname, skiplist, self.has_properties)
        return resource


def _build_superclass_obj(context: Context, shortname: str, superclasses: tuple[str, ...]) -> list[str] | str:
    """Build superclass representation for definition file."""
    if len(superclasses) > 1:
        return [context.reduce_iri(sc, shortname) for sc in superclasses]
    else:
        return context.reduce_iri(superclasses[0], shortname)


def _add_cardinalities(
    context: Context,
    resource: dict[str, Any],
    shortname: str,
    skiplist: list[str],
    has_properties: dict[str, HasProperty],
) -> None:
    """Add cardinalities to the resource definition."""
    cardinalities: list[dict[str, Any]] = []
    for _, hp in has_properties.items():
        if hp.property_id in skiplist:
            continue
        if hp.ptype == Ptype.other or hp.property_id in [
            "knora-api:isPartOf",
            "knora-api:seqnum",
        ]:
            cardinalities.append(hp.to_definition_file_obj(context, shortname))
    if cardinalities:
        resource["cardinalities"] = cardinalities


def create_resource_class_from_json(json_obj: Any) -> ResourceClass:
    """
    Create a ResourceClass from a JSON-LD object.

    Args:
        json_obj: JSON-LD object from DSP API

    Returns:
        ResourceClass instance
    """
    if isinstance(json_obj, list):
        json_obj = json_obj[0]

    if not (json_obj.get("knora-api:isResourceClass") or json_obj.get("knora-api:isStandoffClass")):
        raise BaseError("This is not a resource!")

    if json_obj.get("@id") is None:
        raise BaseError('Resource class has no "@id"!')

    tmp_id = json_obj["@id"].split(":")
    name = tmp_id[1]

    has_properties, superclasses = _extract_superclass_and_properties(json_obj)

    label = create_lang_string_from_json_ld(json_obj.get("rdfs:label")) or create_lang_string()
    comment = create_lang_string_from_json_ld(json_obj.get("rdfs:comment")) or create_lang_string()

    return ResourceClass(
        name=name,
        superclasses=superclasses,
        label=label,
        comment=comment,
        has_properties=has_properties,
    )


def _extract_superclass_and_properties(
    json_obj: dict[str, Any],
) -> tuple[dict[str, HasProperty] | None, tuple[str, ...] | None]:
    """Extract superclasses and has_properties from JSON-LD object."""
    superclasses_obj = json_obj.get("rdfs:subClassOf")
    if superclasses_obj is None:
        return None, None

    supercls = [a for a in superclasses_obj if a.get("@id") is not None]
    superclasses = tuple(a["@id"] for a in supercls)

    has_props = [a for a in superclasses_obj if a.get("@type") == "owl:Restriction"]
    has_properties = dict(create_has_property_from_json(a) for a in has_props)

    # Remove the ...Value stuff from resource pointers: A resource pointer is returned as 2 properties:
    # one a direct link, the other the pointer to a link value
    keys_to_remove = [
        key for key in has_properties if key.endswith("Value") and key.removesuffix("Value") in has_properties
    ]
    for key in keys_to_remove:
        del has_properties[key]

    return has_properties, superclasses if superclasses else None
