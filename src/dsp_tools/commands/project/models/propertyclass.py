from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union
from urllib.parse import quote_plus

import regex

from dsp_tools.commands.project.models.context import Context
from dsp_tools.commands.project.models.helpers import WithId
from dsp_tools.commands.project.models.listnode import ListNode
from dsp_tools.commands.project.models.model import Model
from dsp_tools.models.datetimestamp import DateTimeStamp
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.langstring import LangString
from dsp_tools.utils.connection import Connection


class PropertyClass(Model):
    ROUTE: str = "/v2/ontologies/properties"

    _context: Context
    _iri: str
    _name: str
    _ontology_id: str
    _superproperties: list[str]
    _rdf_object: str
    _rdf_subject: str
    _gui_element: str
    _gui_attributes: dict[str, str]
    _label: LangString
    _comment: LangString
    _editable: bool
    _linkvalue: bool

    def __init__(
        self,
        con: Connection,
        context: Context,
        iri: Optional[str] = None,
        name: Optional[str] = None,
        ontology_id: Optional[str] = None,
        superproperties: Optional[Sequence[Union[PropertyClass, str]]] = None,
        rdf_object: Optional[str] = None,
        rdf_subject: Optional[str] = None,
        gui_element: Optional[str] = None,
        gui_attributes: Optional[dict[str, str]] = None,
        label: Optional[Union[LangString, str]] = None,
        comment: Optional[Union[LangString, str]] = None,
        editable: Optional[bool] = None,
        linkvalue: Optional[bool] = None,
    ):
        super().__init__(con)
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self._context = context
        self._iri = iri
        self._name = name
        self._ontology_id = ontology_id
        if isinstance(superproperties, PropertyClass):
            self._superproperties = list(map(lambda a: a.iri, superproperties))
        else:
            self._superproperties = superproperties
        self._rdf_object = rdf_object
        self._rdf_subject = rdf_subject
        self._gui_element = gui_element
        self._gui_attributes = gui_attributes

        self._label = PropertyClass._init_process_language_value(label, "label")
        self._comment = PropertyClass._init_process_language_value(comment, "comment")

        self._editable = editable
        self._linkvalue = linkvalue

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

    #
    # Here follows a list of getters/setters
    #
    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

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

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        if value is None:
            self._label.empty()  # clear all labels
        elif isinstance(value, LangString):
            self._label = value
        elif isinstance(value, str):
            self._label = LangString(value)
        else:
            raise BaseError("Not a valid LangString")
        self._changed.add("label")

    @property
    def comment(self) -> LangString:
        return self._comment

    @comment.setter
    def comment(self, value: Optional[LangString]) -> None:
        if value is None:
            self._comment.empty()  # clear all comments!
        elif isinstance(value, LangString):
            self._comment = value
        elif isinstance(value, str):
            self._comment = LangString(value)
        else:
            raise BaseError("Not a valid LangString")
        self._changed.add("comment")

    @property
    def editable(self) -> bool:
        return self._editable

    @property
    def linkvalue(self) -> bool:
        return self._linkvalue

    @linkvalue.setter
    def linkvalue(self) -> None:
        raise BaseError('"linkvalue" cannot be modified!')

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
        iri = context.iri_from_prefix(tmp_id[0]) + "#" + tmp_id[1]
        ontology_id = tmp_id[0]
        name = tmp_id[1]

        rdf_object = WithId(json_obj.get(knora_api_iri + ":objectType")).to_string()
        rdf_subject = WithId(json_obj.get(knora_api_iri + ":subjectType")).to_string()
        label = LangString.fromJsonLdObj(json_obj.get(rdfs_iri + ":label"))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs_iri + ":comment"))
        editable = json_obj.get(knora_api_iri + ":isEditable")
        linkvalue = json_obj.get(knora_api_iri + ":isLinkProperty")

        gui_attributes, gui_element = cls._fromJsonObj_get_gui_info(json_obj, salsah_gui_iri)
        superproperties = cls._fromJson_get_superproperties(json_obj, rdfs_iri)

        return cls(
            con=con,
            context=context,
            iri=iri,
            name=name,
            ontology_id=ontology_id,
            superproperties=superproperties,
            rdf_object=rdf_object,
            rdf_subject=rdf_subject,
            gui_element=gui_element,
            gui_attributes=gui_attributes,
            label=label,
            comment=comment,
            editable=editable,
            linkvalue=linkvalue,
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
            gui_element = WithId(json_obj.get(salsah_gui + ":guiElement")).to_string()
            gui_element = gui_element.replace("Pulldown", "List")
            gui_element = gui_element.replace("Radio", "List")
        gui_attributes_list = json_obj.get(salsah_gui + ":guiAttribute")
        gui_attributes: Union[None, dict[str, str]] = None
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

    def _make_full_onto_iri(self) -> tuple[str, str]:
        exp = regex.compile("^http.*")  # It is already a full IRI
        if exp.match(self._ontology_id):
            propid = self._context.prefix_from_iri(self._ontology_id) + ":" + self._name
            ontid = self._ontology_id
        else:
            propid = self._ontology_id + ":" + self._name
            ontid = self._context.iri_from_prefix(self._ontology_id)
        return ontid, propid

    def _resolve_propref(self, resref: str) -> dict[str, str]:
        tmp = resref.split(":")
        if len(tmp) > 1:
            if tmp[0]:
                # return {"@id": resref}  # fully qualified name in the form "prefix:name"
                return {
                    "@id": self._context.get_qualified_iri(resref)
                }  # fully qualified name in the form "prefix:name"
            else:
                return {
                    "@id": self._context.prefix_from_iri(self._ontology_id) + ":" + tmp[1]
                }  # ":name" in current ontology
        else:
            return {"@id": "knora-api:" + resref}  # no ":", must be from knora-api!

    def create(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, PropertyClass]:
        jsonobj = self._toJsonObj_create(last_modification_date)
        result = self._con.post(PropertyClass.ROUTE, jsonobj)
        last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
        return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result["@graph"])

    def _toJsonObj_create(self, lastModificationDate: DateTimeStamp) -> dict[str, Any]:
        ontid, propid = self._make_full_onto_iri()
        if self._name is None:
            raise BaseError("There must be a valid property class name!")
        if self._ontology_id is None:
            raise BaseError("There must be a valid ontology_id given!")
        if self._superproperties is None:
            superproperties = [{"@id": "knora-api:hasValue"}]
        else:
            superproperties = list(map(self._resolve_propref, self._superproperties))
        tmp = {
            "@id": ontid,  # self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": propid,
                    "@type": "owl:ObjectProperty",
                    "rdfs:label": self._label.toJsonLdObj(),
                    "rdfs:subPropertyOf": superproperties,
                }
            ],
            "@context": self._context.toJsonObj(),
        }
        if self._comment:
            tmp["@graph"][0]["rdfs:comment"] = self._comment.toJsonLdObj()
        if self._rdf_subject:
            tmp["@graph"][0]["knora-api:subjectType"] = self._resolve_propref(self._rdf_subject)
        if self._rdf_object:
            tmp["@graph"][0]["knora-api:objectType"] = self._resolve_propref(self._rdf_object)
        if self._gui_element:
            tmp["@graph"][0]["salsah-gui:guiElement"] = {"@id": self._gui_element}
        if self._gui_attributes:
            ga = list(map(lambda x: x[0] + "=" + str(x[1]), self._gui_attributes.items()))
            tmp["@graph"][0]["salsah-gui:guiAttribute"] = ga
        return tmp

    def update(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, PropertyClass]:
        #
        # Note: DSP is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if "label" in self._changed:
            jsonobj = self._toJsonObj_update(last_modification_date, "label")
            result = self._con.put(PropertyClass.ROUTE, jsonobj)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if "comment" in self._changed:
            jsonobj = self._toJsonObj_update(last_modification_date, "comment")
            result = self._con.put(PropertyClass.ROUTE, jsonobj)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if something_changed:
            return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result["@graph"])
        else:
            return last_modification_date, self

    def _toJsonObj_update(self, lastModificationDate: DateTimeStamp, what_changed: str) -> dict[str, Any]:
        ontid, propid = self._make_full_onto_iri()
        tmp = {
            "@id": ontid,  # self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": propid,
                    "@type": "owl:ObjectProperty",
                }
            ],
            "@context": self._context.toJsonObj(),
        }
        if what_changed == "label":
            if not self._label.isEmpty() and "label" in self._changed:
                tmp["@graph"][0]["rdfs:label"] = self._label.toJsonLdObj()
        if what_changed == "comment":
            if not self._comment.isEmpty() and "comment" in self._changed:
                tmp["@graph"][0]["rdfs:comment"] = self._comment.toJsonLdObj()
        return tmp

    def delete(self, last_modification_date: DateTimeStamp) -> DateTimeStamp:
        result = self._con.delete(
            PropertyClass.ROUTE + "/" + quote_plus(self._iri) + "?lastModificationDate=" + str(last_modification_date)
        )
        return DateTimeStamp(result["knora-api:lastModificationDate"])

    def createDefinitionFileObj(self, context: Context, shortname: str) -> dict[str, Any]:
        """
        Create an object that can be used as input for `create_onto()` to create an ontology on a DSP server

        :param context: Context of the ontology
        :param shortname: Shortname of the ontology
        :return: Python object to be jsonfied
        """
        def_file_obj = {"name": self.name}
        if self.rdf_object:
            def_file_obj["name"] = self.name
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

    def _createDefinitionFileObj_gui_attributes(self) -> dict[str, Any]:
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
                    rootnode = ListNode(con=self._con, iri=iri).read()
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
