"""
This module implements reading property classes.
"""

from __future__ import annotations

from typing import Any
from typing import Optional

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.get.legacy_models.context import Context
from dsp_tools.commands.get.legacy_models.helpers import get_json_ld_id
from dsp_tools.commands.get.legacy_models.listnode import ListNode
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import LangString


class PropertyClass:
    """Represents a DSP property class definition."""

    _con: Connection
    _context: Context
    _name: str
    _superproperties: list[str]
    _rdf_object: str
    _rdf_subject: str
    _gui_element: str
    _gui_attributes: dict[str, str]
    _label: LangString
    _comment: LangString

    def __init__(
        self,
        con: Connection,
        context: Context,
        name: Optional[str] = None,
        superproperties: Optional[list[str]] = None,
        rdf_object: Optional[str] = None,
        rdf_subject: Optional[str] = None,
        gui_element: Optional[str] = None,
        gui_attributes: Optional[dict[str, str]] = None,
        label: Optional[LangString | str] = None,
        comment: Optional[LangString | str] = None,
    ):
        self._con = con
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self._context = context
        self._name = name
        self._superproperties = superproperties
        self._rdf_object = rdf_object
        self._rdf_subject = rdf_subject
        self._gui_element = gui_element
        self._gui_attributes = gui_attributes

        self._label = PropertyClass._init_process_language_value(label, "label")
        self._comment = PropertyClass._init_process_language_value(comment, "comment")

    @staticmethod
    def _init_process_language_value(prop_val: None | str | LangString, property: str) -> LangString:
        if prop_val is not None:
            if isinstance(prop_val, str):
                return LangString(prop_val)
            elif isinstance(prop_val, LangString):
                return prop_val
            else:
                raise BaseError(f"Invalid LangString for {property}!")
        else:
            return LangString({})

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def superproperties(self) -> Optional[list[str]]:
        return self._superproperties

    @property
    def rdf_object(self) -> Optional[str]:
        return self._rdf_object

    @property
    def rdf_subject(self) -> Optional[str]:
        return self._rdf_subject

    @property
    def gui_element(self) -> Optional[str]:
        return self._gui_element

    @property
    def gui_attributes(self) -> Optional[dict[str, str]]:
        return self._gui_attributes

    @property
    def label(self) -> LangString:
        return self._label

    @property
    def comment(self) -> LangString:
        return self._comment

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> PropertyClass:
        if isinstance(json_obj, list):
            json_obj = json_obj[0]
        rdfs_iri = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        knora_api_iri = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui_iri = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if not json_obj.get(knora_api_iri + ":isResourceProperty"):
            raise BaseError("This is not a property!")
        if json_obj.get("@id") is None:
            raise BaseError('Property class has no "@id"!')

        tmp_id = json_obj.get("@id").split(":")
        name = tmp_id[1]

        rdf_object = get_json_ld_id(json_obj.get(knora_api_iri + ":objectType"))
        rdf_subject = get_json_ld_id(json_obj.get(knora_api_iri + ":subjectType"))
        label = LangString.fromJsonLdObj(json_obj.get(rdfs_iri + ":label"))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs_iri + ":comment"))

        gui_attributes, gui_element = cls._fromJsonObj_get_gui_info(json_obj, salsah_gui_iri)
        superproperties = cls._fromJson_get_superproperties(json_obj, rdfs_iri)

        return cls(
            con=con,
            context=context,
            name=name,
            superproperties=superproperties,
            rdf_object=rdf_object,
            rdf_subject=rdf_subject,
            gui_element=gui_element,
            gui_attributes=gui_attributes,
            label=label,
            comment=comment,
        )

    @classmethod
    def _fromJson_get_superproperties(cls, json_obj: dict[str, Any], rdfs: str) -> list[str] | None:
        superproperties_obj = json_obj.get(rdfs + ":subPropertyOf")
        if not isinstance(superproperties_obj, list):
            superproperties_obj = [superproperties_obj]  # make a list out of it
        if superproperties_obj:
            return [x["@id"] for x in superproperties_obj if x and x.get("@id")]
        else:
            return None

    @classmethod
    def _fromJsonObj_get_gui_info(cls, json_obj: dict[str, Any], salsah_gui: str) -> tuple[dict[str, str], str]:
        gui_element = None
        if json_obj.get(salsah_gui + ":guiElement") is not None:
            gui_element = get_json_ld_id(json_obj.get(salsah_gui + ":guiElement"))
            gui_element = gui_element.replace("Pulldown", "List")
            gui_element = gui_element.replace("Radio", "List")
        gui_attributes_list = json_obj.get(salsah_gui + ":guiAttribute")
        gui_attributes: None | dict[str, str] = None
        if gui_attributes_list is not None:
            gui_attributes = {}
            if not isinstance(gui_attributes_list, list):
                gui_attributes_list = [gui_attributes_list]
            for ga in gui_attributes_list:
                tmp = ga.split("=")
                if len(tmp) == 1:
                    gui_attributes[tmp[0]] = ""
                else:
                    gui_attributes[tmp[0]] = tmp[1]
        return gui_attributes, gui_element

    def createDefinitionFileObj(self, context: Context, shortname: str) -> dict[str, Any]:
        """
        Create an object that can be used as input for `create_onto()` to create an ontology on a DSP server

        :param context: Context of the ontology
        :param shortname: Shortname of the ontology
        :return: Python object to be jsonfied
        """
        def_file_obj = {"name": self.name}
        if self.superproperties:
            superprops = []
            for sc in self.superproperties:
                superprops.append(context.reduce_iri(sc, shortname))
            def_file_obj["super"] = superprops
        if self.rdf_subject:
            def_file_obj["subject"] = context.reduce_iri(self.rdf_subject, shortname)
        if self.rdf_object:
            def_file_obj["object"] = context.reduce_iri(self.rdf_object, shortname)
        if not self.label.isEmpty():
            def_file_obj["labels"] = self.label.createDefinitionFileObj()
        if not self.comment.isEmpty():
            def_file_obj["comments"] = self.comment.createDefinitionFileObj()
        if self.gui_element:
            def_file_obj["gui_element"] = context.reduce_iri(self.gui_element, shortname)
        if self.gui_attributes:
            gui_elements = self._createDefinitionFileObj_gui_attributes()
            def_file_obj["gui_attributes"] = gui_elements
        return def_file_obj

    def _createDefinitionFileObj_gui_attributes(self) -> dict[str, Any]:  # noqa: PLR0912 (too many branches)
        gui_elements = {}
        for attname, attvalue in self.gui_attributes.items():
            match attname:
                case "size":
                    gui_elements[attname] = int(attvalue)
                case "maxlength":
                    gui_elements[attname] = int(attvalue)
                case "maxsize":
                    gui_elements[attname] = int(attvalue)
                case "hlist":
                    iri = attvalue[1:-1]
                    rootnode = ListNode.read_all_nodes(self._con, iri)
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
