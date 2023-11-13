# pylint: disable=missing-class-docstring,missing-function-docstring

import json
from typing import Any, Optional, Sequence, Union
from urllib.parse import quote_plus

import regex

from dsp_tools.commands.project.models.listnode import ListNode
from dsp_tools.commands.project.models.model import Model
from dsp_tools.commands.project.models.set_encoder import SetEncoder
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.helpers import Actions, Context, DateTimeStamp, WithId
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection


class PropertyClass(Model):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
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
        superproperties: Optional[Sequence[Union["PropertyClass", str]]] = None,
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
        #
        # process label
        #
        if label is not None:
            if isinstance(label, str):
                self._label = LangString(label)
            elif isinstance(label, LangString):
                self._label = label
            else:
                raise BaseError("Invalid LangString for label!")
        else:
            self._label = LangString({})
        #
        # process comment
        #
        if comment is not None:
            if isinstance(comment, str):
                self._comment = LangString(comment)
            elif isinstance(comment, LangString):
                self._comment = comment
            else:
                raise BaseError("Invalid LangString for comment!")
        else:
            self._comment = LangString({})

        self._editable = editable
        self._linkvalue = linkvalue

    #
    # Here follows a list of getters/setters
    #
    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        raise BaseError('"name" cannot be modified!')

    @property
    def iri(self) -> Optional[str]:
        return self._iri

    @iri.setter
    def iri(self, value: str) -> None:
        raise BaseError('"iri" cannot be modified!')

    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def superproperties(self) -> Optional[list[str]]:
        return self._superproperties

    @superproperties.setter
    def superproperties(self, value: str) -> None:
        raise BaseError('"superproperties" cannot be modified!')

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
        else:
            if isinstance(value, LangString):
                self._label = value
            elif isinstance(value, str):
                self._label = LangString(value)
            else:
                raise BaseError("Not a valid LangString")
        self._changed.add("label")

    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        self._label[lang] = value
        self._changed.add("label")

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        del self._label[lang]
        self._changed.add("label")

    @property
    def comment(self) -> LangString:
        return self._comment

    @comment.setter
    def comment(self, value: Optional[LangString]) -> None:
        if value is None:
            self._comment.empty()  # clear all comments!
        else:
            if isinstance(value, LangString):
                self._comment = value
            elif isinstance(value, str):
                self._comment = LangString(value)
            else:
                raise BaseError("Not a valid LangString")
        self._changed.add("comment")

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        self._comment[lang] = value
        self._changed.add("comment")

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self._comment[lang]
        self._changed.add("comment")

    @property
    def editable(self) -> bool:
        return self._editable

    @editable.setter
    def editable(self, value: bool) -> None:
        raise BaseError('"editable" cannot be modified!')

    @property
    def linkvalue(self) -> bool:
        return self._linkvalue

    @linkvalue.setter
    def linkvalue(self) -> None:
        raise BaseError('"linkvalue" cannot be modified!')

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> "PropertyClass":
        if isinstance(json_obj, list):
            json_obj = json_obj[0]
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if not json_obj.get(knora_api + ":isResourceProperty"):
            raise BaseError("This is not a property!")
        if json_obj.get("@id") is None:
            raise BaseError('Property class has no "@id"!')
        tmp_id = json_obj.get("@id").split(":")
        iri = context.iri_from_prefix(tmp_id[0]) + "#" + tmp_id[1]
        ontology_id = tmp_id[0]
        name = tmp_id[1]
        superproperties_obj = json_obj.get(rdfs + ":subPropertyOf")
        superproperties: list[Union[None, str]]
        if not isinstance(superproperties_obj, list):
            superproperties_obj = [superproperties_obj]  # make a list out of it
        if superproperties_obj:
            superproperties = [x["@id"] for x in superproperties_obj if x and x.get("@id")]
        else:
            superproperties = None
        rdf_object = WithId(json_obj.get(knora_api + ":objectType")).str()
        rdf_subject = WithId(json_obj.get(knora_api + ":subjectType")).str()
        label = LangString.fromJsonLdObj(json_obj.get(rdfs + ":label"))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs + ":comment"))
        gui_element = None
        if json_obj.get(salsah_gui + ":guiElement") is not None:
            gui_element = WithId(json_obj.get(salsah_gui + ":guiElement")).str()
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

        editable = json_obj.get(knora_api + ":isEditable")
        linkvalue = json_obj.get(knora_api + ":isLinkProperty")
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

    def toJsonObj(self, lastModificationDate: DateTimeStamp, action: Actions, what: Optional[str] = None) -> Any:
        def resolve_propref(resref: str) -> dict[str, str]:
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

        tmp = {}
        exp = regex.compile("^http.*")  # It is already a fully IRI
        if exp.match(self._ontology_id):
            propid = self._context.prefix_from_iri(self._ontology_id) + ":" + self._name
            ontid = self._ontology_id
        else:
            propid = self._ontology_id + ":" + self._name
            ontid = self._context.iri_from_prefix(self._ontology_id)
        if action == Actions.Create:
            if self._name is None:
                raise BaseError("There must be a valid property class name!")
            if self._ontology_id is None:
                raise BaseError("There must be a valid ontology_id given!")
            if self._superproperties is None:
                superproperties = [{"@id": "knora-api:hasValue"}]
            else:
                superproperties = list(map(resolve_propref, self._superproperties))

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
                tmp["@graph"][0]["knora-api:subjectType"] = resolve_propref(self._rdf_subject)
            if self._rdf_object:
                tmp["@graph"][0]["knora-api:objectType"] = resolve_propref(self._rdf_object)
            if self._gui_element:
                tmp["@graph"][0]["salsah-gui:guiElement"] = {"@id": self._gui_element}
            if self._gui_attributes:
                ga = list(map(lambda x: x[0] + "=" + str(x[1]), self._gui_attributes.items()))
                tmp["@graph"][0]["salsah-gui:guiAttribute"] = ga
        elif action == Actions.Update:
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
            if what == "label":
                if not self._label.isEmpty() and "label" in self._changed:
                    tmp["@graph"][0]["rdfs:label"] = self._label.toJsonLdObj()
            if what == "comment":
                if not self._comment.isEmpty() and "comment" in self._changed:
                    tmp["@graph"][0]["rdfs:comment"] = self._comment.toJsonLdObj()

        return tmp

    def create(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, "PropertyClass"]:
        jsonobj = self.toJsonObj(last_modification_date, Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=2)
        result = self._con.post(PropertyClass.ROUTE, jsondata)
        last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
        return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result["@graph"])

    def update(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, "PropertyClass"]:
        #
        # Note: DSP is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if "label" in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, "label")
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self._con.put(PropertyClass.ROUTE, jsondata)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if "comment" in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, "comment")
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self._con.put(PropertyClass.ROUTE, jsondata)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if something_changed:
            return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result["@graph"])
        else:
            return last_modification_date, self

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
            gui_elements = {}
            for attname, attvalue in self.gui_attributes.items():
                if attname == "size":
                    gui_elements[attname] = int(attvalue)
                elif attname == "maxlength":
                    gui_elements[attname] = int(attvalue)
                elif attname == "maxsize":
                    gui_elements[attname] = int(attvalue)
                elif attname == "hlist":
                    iri = attvalue[1:-1]
                    rootnode = ListNode(con=self._con, iri=iri).read()
                    gui_elements[attname] = rootnode.name
                elif attname == "numprops":
                    gui_elements[attname] = int(attvalue)
                elif attname == "ncolors":
                    gui_elements[attname] = int(attvalue)
                elif attname == "cols":
                    gui_elements[attname] = int(attvalue)
                elif attname == "rows":
                    gui_elements[attname] = int(attvalue)
                elif attname == "width":
                    gui_elements[attname] = str(attvalue)
                elif attname == "wrap":
                    gui_elements[attname] = str(attvalue)
                elif attname == "max":
                    gui_elements[attname] = float(attvalue)
                elif attname == "min":
                    gui_elements[attname] = float(attvalue)
                else:
                    gui_elements[attname] = str(attvalue)
            def_file_obj["gui_attributes"] = gui_elements
        return def_file_obj
