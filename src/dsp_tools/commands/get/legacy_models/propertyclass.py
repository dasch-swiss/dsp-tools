"""
This module implements reading property classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.context import Context
from dsp_tools.commands.get.legacy_models.helpers import get_json_ld_id
from dsp_tools.commands.get.legacy_models.listnode import read_all_nodes
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json_ld


@dataclass(frozen=True)
class PropertyClass:
    """Represents a DSP property class definition."""

    name: str
    superproperties: tuple[str, ...] | None
    rdf_object: str | None
    rdf_subject: str | None
    gui_element: str | None
    gui_attributes: dict[str, str] | None
    label: LangString
    comment: LangString

    def to_definition_file_obj(self, con: Connection, context: Context, shortname: str) -> dict[str, Any]:
        """
        Create an object that can be used as input for `create_onto()` to create an ontology on a DSP server.

        Args:
            con: Connection instance for resolving hlist references
            context: Context of the ontology
            shortname: Shortname of the ontology

        Returns:
            Python object to be jsonfied
        """
        def_file_obj: dict[str, Any] = {"name": self.name}
        if self.superproperties:
            superprops = [context.reduce_iri(sc, shortname) for sc in self.superproperties]
            def_file_obj["super"] = superprops
        if self.rdf_subject:
            def_file_obj["subject"] = context.reduce_iri(self.rdf_subject, shortname)
        if self.rdf_object:
            def_file_obj["object"] = context.reduce_iri(self.rdf_object, shortname)
        if not self.label.is_empty():
            def_file_obj["labels"] = self.label.to_definition_file_obj()
        if not self.comment.is_empty():
            def_file_obj["comments"] = self.comment.to_definition_file_obj()
        if self.gui_element:
            def_file_obj["gui_element"] = context.reduce_iri(self.gui_element, shortname)
        if self.gui_attributes:
            gui_elements = _build_gui_attributes(con, self.gui_attributes)
            def_file_obj["gui_attributes"] = gui_elements
        return def_file_obj


def create_property_class_from_json(json_obj: dict[str, Any] | list[dict[str, Any]]) -> PropertyClass:
    """
    Create a PropertyClass from a JSON-LD object returned by DSP API.

    Args:
        json_obj: JSON-LD object from DSP API

    Returns:
        PropertyClass instance
    """
    obj: dict[str, Any] = json_obj[0] if isinstance(json_obj, list) else json_obj

    if not obj.get("knora-api:isResourceProperty"):
        raise BaseError("This is not a property!")
    if obj.get("@id") is None:
        raise BaseError('Property class has no "@id"!')

    tmp_id = obj["@id"].split(":")
    name: str = tmp_id[1]

    rdf_object = get_json_ld_id(obj.get("knora-api:objectType"))
    rdf_subject = get_json_ld_id(obj.get("knora-api:subjectType"))
    label = create_lang_string_from_json_ld(obj.get("rdfs:label")) or create_lang_string()
    comment = create_lang_string_from_json_ld(obj.get("rdfs:comment")) or create_lang_string()

    gui_attributes, gui_element = _extract_gui_info(obj)
    superproperties = _extract_superproperties(obj)

    return PropertyClass(
        name=name,
        superproperties=superproperties,
        rdf_object=rdf_object,
        rdf_subject=rdf_subject,
        gui_element=gui_element,
        gui_attributes=gui_attributes,
        label=label,
        comment=comment,
    )


def _extract_superproperties(json_obj: dict[str, Any]) -> tuple[str, ...] | None:
    """Extract superproperties from JSON-LD object."""
    superproperties_obj = json_obj.get("rdfs:subPropertyOf")
    if not isinstance(superproperties_obj, list):
        superproperties_obj = [superproperties_obj]
    if superproperties_obj:
        props = [x["@id"] for x in superproperties_obj if x and x.get("@id")]
        return tuple(props) if props else None
    return None


def _extract_gui_info(json_obj: dict[str, Any]) -> tuple[dict[str, str] | None, str | None]:
    """Extract GUI element and attributes from JSON-LD object."""
    gui_element: str | None = None
    gui_element_obj = json_obj.get("salsah-gui:guiElement")
    if gui_element_obj is not None:
        gui_element = get_json_ld_id(gui_element_obj)
        if gui_element:
            gui_element = gui_element.replace("Pulldown", "List")
            gui_element = gui_element.replace("Radio", "List")

    gui_attributes_list = json_obj.get("salsah-gui:guiAttribute")
    gui_attributes: dict[str, str] | None = None
    if gui_attributes_list is not None:
        gui_attributes = {}
        if not isinstance(gui_attributes_list, list):
            gui_attributes_list = [gui_attributes_list]
        for ga in gui_attributes_list:
            parts = str(ga).split("=")
            if len(parts) == 1:
                gui_attributes[parts[0]] = ""
            else:
                gui_attributes[parts[0]] = parts[1]
    return gui_attributes, gui_element


def _build_gui_attributes(con: Connection, gui_attributes: dict[str, str]) -> dict[str, Any]:  # noqa: PLR0912
    """Build gui_attributes dict for definition file, resolving hlist references."""
    gui_elements: dict[str, Any] = {}
    for attname, attvalue in gui_attributes.items():
        match attname:
            case "size":
                gui_elements[attname] = int(attvalue)
            case "maxlength":
                gui_elements[attname] = int(attvalue)
            case "maxsize":
                gui_elements[attname] = int(attvalue)
            case "hlist":
                iri = attvalue[1:-1]
                rootnode = read_all_nodes(con, iri)
                gui_elements[attname] = rootnode.name
            case "numprops":
                gui_elements[attname] = int(attvalue)
            case "ncolors":
                gui_elements[attname] = int(attvalue)
            case "cols":
                gui_elements[attname] = int(attvalue)
            case "rows":
                gui_elements[attname] = int(attvalue)
            case "width":
                gui_elements[attname] = str(attvalue)
            case "wrap":
                gui_elements[attname] = str(attvalue)
            case "max":
                gui_elements[attname] = float(attvalue)
            case "min":
                gui_elements[attname] = float(attvalue)
            case _:
                gui_elements[attname] = str(attvalue)
    return gui_elements
