"""
This model implements the handling of resource classes. It contains two classes that work closely together:
    * "HasProperty" deals with the association of Property-instances with the Resource-instances. This association
      is done using the "cardinality"-clause
    * "ResourceClass" is the main class representing a DSP resource class.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Any
from typing import Optional
from typing import Union

import regex

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.helpers import Cardinality
from dsp_tools.commands.project.legacy_models.model import Model
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.legacy_models.langstring import LangString


class HasProperty(Model):
    ROUTE: str = "/v2/ontologies/cardinalities"

    class Ptype(Enum):
        system = 1
        knora = 2
        other = 3

    _context: Context
    _ontology_id: str
    _property_id: str
    _resclass_id: str
    _cardinality: Cardinality
    _gui_order: int
    _ptype: Ptype

    def __init__(
        self,
        con: Connection,
        context: Context,
        ontology_id: Optional[str] = None,
        property_id: Optional[str] = None,
        resclass_id: Optional[str] = None,
        cardinality: Optional[Cardinality] = None,
        gui_order: Optional[int] = None,
        ptype: Optional[Ptype] = None,
    ):
        super().__init__(con)
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self._context = context
        if ontology_id is not None:
            self._ontology_id = context.iri_from_prefix(ontology_id)
        else:
            self._ontology_id = None
        self._property_id = property_id
        self._resclass_id = resclass_id
        self._cardinality = cardinality
        self._gui_order = gui_order
        self._ptype = ptype
        self._changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: Optional[str]) -> None:
        self._ontology_id = value

    @property
    def property_id(self) -> Optional[str]:
        return self._property_id

    @property
    def resclass_id(self) -> Optional[str]:
        return self._resclass_id

    @resclass_id.setter
    def resclass_id(self, value: Optional[str]) -> None:
        self._resclass_id = value

    @property
    def cardinality(self) -> Optional[Cardinality]:
        return self._cardinality

    @cardinality.setter
    def cardinality(self, value: Optional[Cardinality]) -> None:
        self._cardinality = value
        self._changed.add("cardinality")

    @property
    def gui_order(self) -> Optional[int]:
        return self._gui_order

    @gui_order.setter
    def gui_order(self, value: int) -> None:
        self._gui_order = value
        self._changed.add("gui_order")

    @property
    def ptype(self) -> Ptype:
        return self._ptype

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, jsonld_obj: dict[str, Any]) -> tuple[str, HasProperty]:
        rdf_iri = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs_iri = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl_iri = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        knora_api_iri = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui_iri = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if jsonld_obj.get("@type") is None or jsonld_obj.get("@type") != owl_iri + ":Restriction":
            raise BaseError("Expected restriction type")

        cardinality = cls._fromJsonObj_get_cardinality(jsonld_obj, owl_iri)

        ontology_id, property_id, ptype = cls._fromJsonObj_get_prop_type_iri(
            context, jsonld_obj, knora_api_iri, owl_iri, rdf_iri, rdfs_iri
        )

        gui_order: int = None
        if jsonld_obj.get(salsah_gui_iri + ":guiOrder") is not None:
            gui_order = jsonld_obj[salsah_gui_iri + ":guiOrder"]
        return property_id, cls(
            con=con,
            context=context,
            ontology_id=ontology_id,
            property_id=property_id,
            cardinality=cardinality,
            gui_order=gui_order,
            ptype=ptype,
        )

    @staticmethod
    def _fromJsonObj_get_prop_type_iri(
        context: Context, jsonld_obj: dict[str, Any], knora_api_iri: str, owl_iri: str, rdf_iri: str, rdfs_iri: str
    ) -> tuple[str, str, HasProperty.Ptype]:
        property_id: str
        ptype: HasProperty.Ptype
        ontology_id: Optional[str] = None
        if jsonld_obj.get(owl_iri + ":onProperty") is None:
            raise BaseError("No property IRI given")
        p = jsonld_obj[owl_iri + ":onProperty"].get("@id")
        if p is None:
            raise BaseError("No property IRI given")
        pp = p.split(":")
        if pp[0] == rdf_iri or pp[0] == rdfs_iri or pp[0] == owl_iri:
            ptype = HasProperty.Ptype.system
        elif pp[0] == knora_api_iri:
            ptype = HasProperty.Ptype.knora
        else:
            ptype = HasProperty.Ptype.other
            ontology_id = context.iri_from_prefix(pp[0])
        property_id = p
        return ontology_id, property_id, ptype

    @staticmethod
    def _fromJsonObj_get_cardinality(jsonld_obj: dict[str, Any], owl_iri: str):
        cardinality: Cardinality
        if jsonld_obj.get(owl_iri + ":cardinality") is not None:
            cardinality = Cardinality.C_1
        elif jsonld_obj.get(owl_iri + ":maxCardinality") is not None:
            cardinality = Cardinality.C_0_1
        elif jsonld_obj.get(owl_iri + ":minCardinality") is not None:
            if jsonld_obj.get(owl_iri + ":minCardinality") == 0:
                cardinality = Cardinality.C_0_n
            elif jsonld_obj.get(owl_iri + ":minCardinality") == 1:
                cardinality = Cardinality.C_1_n
            else:
                raise BaseError("Problem with cardinality")
        else:
            raise BaseError("Problem with cardinality")
        return cardinality

    def create(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, ResourceClass]:
        if self._ontology_id is None:
            raise BaseError("Ontology id required")
        if self._property_id is None:
            raise BaseError("Property id required")
        if self._cardinality is None:
            raise BaseError("Cardinality id required")

        jsonobj = self._toJsonObj_create(last_modification_date)
        result = self._con.post(HasProperty.ROUTE, jsonobj)
        last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
        return last_modification_date, ResourceClass.fromJsonObj(self._con, self._context, result["@graph"])

    def update(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, ResourceClass]:
        if self._ontology_id is None:
            raise BaseError("Ontology id required")
        if self._property_id is None:
            raise BaseError("Property id required")
        if self._cardinality is None:
            raise BaseError("Cardinality id required")
        jsonobj = self._toJsonObj_update(last_modification_date)
        result = self._con.put(HasProperty.ROUTE, jsonobj)
        last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
        return last_modification_date, ResourceClass.fromJsonObj(self._con, self._context, result["@graph"])

    def _toJsonObj_update(self, lastModificationDate: DateTimeStamp) -> dict[str, Any]:
        occurrence = self._toJsonObj_get_owl_cardinality()
        tmp = {
            "@id": self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": self._resclass_id,
                    "@type": "owl:Class",
                    "rdfs:subClassOf": {
                        "@type": "owl:Restriction",
                        occurrence[0]: occurrence[1],
                        "owl:onProperty": {"@id": self._property_id},
                    },
                }
            ],
            "@context": self._context.toJsonObj(),
        }
        if self._gui_order is not None and "gui_order" in self._changed:
            tmp["@graph"][0]["rdfs:subClassOf"]["salsah-gui:guiOrder"] = self._gui_order
        return tmp

    def _toJsonObj_create(self, lastModificationDate: DateTimeStamp) -> dict[str, Any]:
        occurrence = self._toJsonObj_get_owl_cardinality()
        tmp = {
            "@id": self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": self._resclass_id,
                    "@type": "owl:Class",
                    "rdfs:subClassOf": {
                        "@type": "owl:Restriction",
                        occurrence[0]: occurrence[1],
                        "owl:onProperty": {"@id": self._property_id},
                    },
                }
            ],
            "@context": self._context.toJsonObj(),
        }
        if self._gui_order is not None:
            tmp["@graph"][0]["rdfs:subClassOf"]["salsah-gui:guiOrder"] = self._gui_order
        return tmp

    def _toJsonObj_get_owl_cardinality(self) -> tuple[str, int]:
        if self._cardinality is None:
            raise BaseError("There must be a cardinality given!")
        switcher = {
            Cardinality.C_1: ("owl:cardinality", 1),
            Cardinality.C_0_1: ("owl:maxCardinality", 1),
            Cardinality.C_0_n: ("owl:minCardinality", 0),
            Cardinality.C_1_n: ("owl:minCardinality", 1),
        }
        return switcher.get(self._cardinality)

    def createDefinitionFileObj(self, context: Context, shortname: str) -> dict[str, Any]:
        cardinality = {}
        if self._ptype == HasProperty.Ptype.other or self.property_id in [
            "knora-api:isPartOf",
            "knora-api:seqnum",
        ]:
            cardinality["propname"] = context.reduce_iri(self._property_id, shortname)
            cardinality["cardinality"] = self._cardinality.value
            if self._gui_order is not None:
                cardinality["gui_order"] = self._gui_order
        return cardinality


class ResourceClass(Model):
    """
    This class represents a DSP resource class

    Attributes
    ----------

    con : Connection
        A Connection instance to a DSP server

    iri : str
        IRI of the ResourceClass [readonly, cannot be modified after creation of instance]

    name: str
        The name of the resource class, e.g. "Book", "Person", "Portait". Usually these names start
        with a capital letter

    ontology_id: str
        The IRI/Id of the ontology this resource class belongs to

    superclasses: str, list[str]
        This is a list of superclasses for this resource class. Usually a project specific class must at least
        be a subclass of "Resource", but can be subclassed of any other valid resource class. In addition, external
        ontologies may be referenced:
        e.g.:
        ```
        "super": "Resource"

        "super": ":MySpecialTYpe"

        "super": [":MySpecialType", "dcterms:BibliographicResource"]
        ```

    label: language dependent string, that is a dict like {"en": "Biblography", "de": "Literaturverzeichnis"}
        A label (human readable name) for the resource

    comment: language dependent string, that is a dict like {"en": "a comment", "de": "Ein Kommentar"}
        A commentary to further explain what this resource class is used for

    permission: str
        The default permissions to be used if an instance of this resource class is being created

    has_properties: dict[str, HasProperty]
        Holds a dict with the property names as keys and a HasProperty instance. HasProperty holds
        the information, how this resource class uses this property (basically the cardinality)

    changed: bool
        is set to True, if one of the fields has been chaned by the user (internal use only!)


    Methods
    -------

    getProperty: Get information about a property defined for this resource class
        getPropertery(prop_id: str) -> HasProperty
        returns a HasProperty-instance

    addProperty: Add a new property to the resource class
        addProperty(property_id: str, cardinality: Cardinality, last_modification_date: DateTimeStamp)
        -> Optional[DateTimeStamp]

    create: Create a new resource class on the connected server

    update: Update the information of a resource class on the connected server

    delete: Mark a resource class as deleted (on the connected server)

    createDefinitionFileObj: Create an object suitable for jsonification that conforms the the DSP-TOOLS ontology tools

    print: Print the content of this class to the console

    """

    ROUTE: str = "/v2/ontologies/classes"

    _context: Context
    _iri: str
    _name: str
    _ontology_id: str
    _superclasses: list[str]
    _label: LangString
    _comment: LangString
    _permissions: str
    _has_properties: dict[str, HasProperty]

    def __init__(
        self,
        con: Connection,
        context: Context,
        iri: Optional[str] = None,
        name: Optional[str] = None,
        ontology_id: Optional[str] = None,
        superclasses: Optional[Sequence[Union[ResourceClass, str]]] = None,
        label: Optional[Union[LangString, str]] = None,
        comment: Optional[Union[LangString, str]] = None,
        permissions: Optional[str] = None,
        has_properties: Optional[dict[str, HasProperty]] = None,
    ):
        """
        Create an instance of  ResourceClass

        :param con:
        :param context:
        :param iri:
        :param name:
        :param ontology_id:
        :param superclasses:
        :param label:
        :param comment:
        :param permissions:
        :param has_properties:
        """
        super().__init__(con)
        self._context = context
        self._iri = iri
        self._name = name
        if ontology_id is not None:
            self._ontology_id = context.iri_from_prefix(ontology_id)
        if isinstance(superclasses, ResourceClass):
            self._superclasses = list(map(lambda a: a.iri, superclasses))
        else:
            self._superclasses = superclasses

        self._label = self._check_process_langstring(label, "label")
        self._comment = self._check_process_langstring(comment, "comment")
        self._permissions = permissions
        self._has_properties = has_properties
        self._changed = set()

    @staticmethod
    def _check_process_langstring(langstring_to_check: None | str | LangString, what: str) -> LangString:
        if langstring_to_check is not None:
            if isinstance(langstring_to_check, str):
                return LangString(langstring_to_check)
            elif isinstance(langstring_to_check, LangString):
                return langstring_to_check
            else:
                raise BaseError(f"Invalid LangString for {what}!")
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
    def superclasses(self) -> Optional[list[str]]:
        return self._superclasses

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
    def permissions(self) -> Optional[str]:
        return self._permissions

    @property
    def has_properties(self) -> dict[str, HasProperty]:
        return self._has_properties

    def getProperty(self, property_id: str) -> Optional[HasProperty]:
        if self._has_properties is None:
            return None
        else:
            return self._has_properties.get(self._context.get_prefixed_iri(property_id))

    def addProperty(
        self,
        last_modification_date: DateTimeStamp,
        property_id: str,
        cardinality: Cardinality,
        gui_order: Optional[int] = None,
    ) -> DateTimeStamp:
        if self._has_properties.get(property_id) is None:
            latest_modification_date, resclass = HasProperty(
                con=self._con,
                context=self._context,
                ontology_id=self._ontology_id,
                property_id=property_id,
                resclass_id=self.iri,
                cardinality=cardinality,
                gui_order=gui_order,
            ).create(last_modification_date)
            hp = resclass.getProperty(property_id)
            hp.ontology_id = self._context.iri_from_prefix(self._ontology_id)
            hp.resclass_id = self._iri
            self._has_properties[hp.property_id] = hp
            return latest_modification_date
        else:
            raise BaseError("Property already has cardinality in this class! " + property_id)

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> ResourceClass:
        if isinstance(json_obj, list):
            json_obj = json_obj[0]
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")

        if not (json_obj.get(knora_api + ":isResourceClass") or json_obj.get(knora_api + ":isStandoffClass")):
            raise BaseError("This is not a resource!")

        if json_obj.get("@id") is None:
            raise BaseError('Resource class has no "@id"!')

        tmp_id = json_obj.get("@id").split(":")
        iri = context.iri_from_prefix(tmp_id[0]) + "#" + tmp_id[1]
        ontology_id = tmp_id[0]
        name = tmp_id[1]

        has_properties, superclasses = cls._fromJsonObj_get_superclass(con, context, json_obj, rdfs, owl)

        label = LangString.fromJsonLdObj(json_obj.get(rdfs + ":label"))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs + ":comment"))
        return cls(
            con=con,
            context=context,
            name=name,
            iri=iri,
            ontology_id=ontology_id,
            superclasses=superclasses,
            label=label,
            comment=comment,
            has_properties=has_properties,
        )

    @staticmethod
    def _fromJsonObj_get_superclass(
        con: Connection, context: Context, json_obj: dict[str, Any], rdfs: str, owl: str
    ) -> tuple[None | dict[str, HasProperty], None | list[str]]:
        superclasses_obj = json_obj.get(rdfs + ":subClassOf")
        if superclasses_obj is not None:
            supercls = list(filter(lambda a: a.get("@id") is not None, superclasses_obj))
            superclasses = list(map(lambda a: a["@id"], supercls))
            has_props = list(filter(lambda a: a.get("@type") == (owl + ":Restriction"), superclasses_obj))
            has_properties = dict(map(lambda a: HasProperty.fromJsonObj(con, context, a), has_props))
            #
            # now remove the ...Value stuff from resource pointers: A resource pointer is returned as 2 properties:
            # one a direct link, the other the pointer to a link value
            #
            tmp = dict(has_properties)
            for key in tmp.keys():
                if key.endswith("Value"):
                    key_without_value = key.removesuffix("Value")
                    if key_without_value in has_properties:
                        del has_properties[key]
        else:
            superclasses = None
            has_properties = None
        return has_properties, superclasses

    def create(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, ResourceClass]:
        jsonobj = self._toJsonObj_create(last_modification_date)
        result = self._con.post(ResourceClass.ROUTE, jsonobj)
        last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
        return last_modification_date, ResourceClass.fromJsonObj(self._con, self._context, result["@graph"])

    def update(self, last_modification_date: DateTimeStamp) -> tuple[DateTimeStamp, ResourceClass]:
        #
        # Note: DSP is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if "label" in self._changed:
            jsonobj = self._toJsonObj_update(last_modification_date, "label")
            result = self._con.put(ResourceClass.ROUTE, jsonobj)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if "comment" in self._changed:
            jsonobj = self._toJsonObj_update(last_modification_date, "comment")
            result = self._con.put(ResourceClass.ROUTE, jsonobj)
            last_modification_date = DateTimeStamp(result["knora-api:lastModificationDate"])
            something_changed = True
        if something_changed:
            return last_modification_date, ResourceClass.fromJsonObj(self._con, self._context, result["@graph"])
        else:
            return last_modification_date, self

    def _toJsonObj_update(self, lastModificationDate: DateTimeStamp, what_changed: str) -> dict[str, Any]:
        ontid, resid = self._get_onto_res_iri()
        tmp = {
            "@id": ontid,  # self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": resid,
                    "@type": "owl:Class",
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

    def _toJsonObj_create(self, lastModificationDate: DateTimeStamp) -> dict[str, Any]:
        ontid, resid = self._get_onto_res_iri()
        if self._name is None:
            raise BaseError("There must be a valid resource class name!")
        if self._ontology_id is None:
            raise BaseError("There must be a valid ontology_id given!")
        if self._superclasses is None:
            superclasses = [{"@id": "knora-api:Resource"}]
        else:
            superclasses = list(map(self._resolve_resref, self._superclasses))
        if self._label is None or self._label.isEmpty():
            self._label = LangString("no label available")
        tmp = {
            "@id": ontid,  # self._ontology_id,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
            "@graph": [
                {
                    "@id": resid,
                    "@type": "owl:Class",
                    "rdfs:label": self._label.toJsonLdObj(),
                    "rdfs:subClassOf": superclasses,
                }
            ],
            "@context": self._context.toJsonObj(),
        }
        if self._comment:
            tmp["@graph"][0]["rdfs:comment"] = self._comment.toJsonLdObj()
        return tmp

    def _get_onto_res_iri(self) -> tuple[str, str]:
        exp = regex.compile("^http.*")  # It is already a fully IRI
        if exp.match(self._ontology_id):
            resid = self._context.prefix_from_iri(self._ontology_id) + ":" + self._name
            ontid = self._ontology_id
        else:
            resid = self._ontology_id + ":" + self._name
            ontid = self._context.iri_from_prefix(self._ontology_id)
        return ontid, resid

    def _resolve_resref(self, resref: str) -> dict[str, str]:
        tmp = resref.split(":")
        if len(tmp) > 1:
            if tmp[0] and self._context.iri_from_prefix(tmp[0]) != self._ontology_id:
                self._context.add_context(tmp[0])
                return {"@id": resref}  # fully qualified name in the form "prefix:name"
            else:
                return {
                    "@id": self._context.prefix_from_iri(self._ontology_id) + ":" + tmp[1]
                }  # ":name" in current ontology
        else:
            return {"@id": "knora-api:" + resref}  # no ":", must be from knora-api!

    def createDefinitionFileObj(self, context: Context, shortname: str, skiplist: list[str]) -> dict[str, Any]:
        resource = {"name": self._name}
        if self._superclasses:
            resource["super"] = self._create_DefinitionFileObj_superclass(context, shortname)
        resource["labels"] = self._label.createDefinitionFileObj()
        if not self._comment.isEmpty():
            resource["comments"] = self._comment.createDefinitionFileObj()
        if self._has_properties:
            self._create_DefinitionFileObj_cardinalities(context, resource, shortname, skiplist)
        return resource

    def _create_DefinitionFileObj_cardinalities(
        self, context: Context, resource: dict[str, str], shortname: str, skiplist: list[str]
    ) -> dict[str, Any]:
        cardinalities: list[dict[str, Any]] = []
        for _, hp in self._has_properties.items():
            if hp.property_id in skiplist:
                continue
            if hp.ptype == HasProperty.Ptype.other or hp.property_id in [
                "knora-api:isPartOf",
                "knora-api:seqnum",
            ]:
                cardinalities.append(hp.createDefinitionFileObj(context, shortname))
        if cardinalities:
            resource["cardinalities"] = cardinalities
        return resource

    def _create_DefinitionFileObj_superclass(self, context: Context, shortname: str) -> list[str] | str:
        if len(self._superclasses) > 1:
            superclasses = []
            for sc in self._superclasses:
                superclasses.append(context.reduce_iri(sc, shortname))
        else:
            superclasses = context.reduce_iri(self._superclasses[0], shortname)
        return superclasses
