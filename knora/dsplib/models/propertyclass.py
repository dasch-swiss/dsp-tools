import json
import re
from typing import List, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus

from pystrict import strict

from .connection import Connection
from .helpers import Actions, BaseError, Context, LastModificationDate, WithId
from .langstring import Languages, LangString
from .listnode import ListNode
from .model import Model
from ..utils.set_encoder import SetEncoder


@strict
class PropertyClass(Model):
    _context: Context
    _id: str
    _name: str
    _ontology_id: str
    _superproperties: List[str]
    _object: str
    _subject: str
    _gui_element: str
    _gui_attributes: Dict[str, str]
    _label: LangString
    _comment: LangString
    _editable: bool
    _linkvalue: bool

    def __init__(self,
                 con: Connection,
                 context: Context,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 ontology_id: Optional[str] = None,
                 superproperties: Optional[List[Union['PropertyClass', str]]] = None,
                 object: Optional[str] = None,
                 subject: Optional[str] = None,
                 gui_element: Optional[str] = None,
                 gui_attributes: Optional[Dict[str, str]] = None,
                 label: Optional[Union[LangString, str]] = None,
                 comment: Optional[Union[LangString, str]] = None,
                 editable: Optional[bool] = None,
                 linkvalue: Optional[bool] = None):
        super().__init__(con)
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self._context = context
        self._id = id
        self._name = name
        self._ontology_id = ontology_id
        if isinstance(superproperties, PropertyClass):
            self._superproperties = list(map(lambda a: a.id, superproperties))
        else:
            self._superproperties = superproperties
        self._object = object
        self._subject = subject
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
                raise BaseError('Invalid LangString for label!')
        else:
            self._label = None
        #
        # process comment
        #
        if comment is not None:
            if isinstance(comment, str):
                self._comment = LangString(comment)
            elif isinstance(comment, LangString):
                self._comment = comment
            else:
                raise BaseError('Invalid LangString for comment!')
        else:
            self._comment = None

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
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('"id" cannot be modified!')

    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def superproperties(self) -> Optional[List[str]]:
        return self._superproperties

    @superproperties.setter
    def superproperties(self, value: str) -> None:
        raise BaseError('"superproperties" cannot be modified!')

    @property
    def object(self) -> Optional[str]:
        return self._object

    @object.setter
    def object(self, value: Any):
        raise BaseError('"object" cannot be modified!')

    @property
    def subject(self) -> Optional[str]:
        return self._subject

    @subject.setter
    def subject(self, value: Any):
        raise BaseError('"subject" cannot be modified!')

    @property
    def gui_element(self) -> Optional[str]:
        return self._gui_element

    @gui_element.setter
    def gui_element(self, value: str) -> None:
        self._gui_element = value
        self._changed.append('gui_element')

    @property
    def gui_attributes(self) -> Optional[Dict[str, str]]:
        return self._gui_attributes

    @gui_attributes.setter
    def gui_attributes(self, value: List[Dict[str, str]]) -> None:
        self._gui_attributes = value
        self._changed.append('gui_attributes')

    def addGuiAttribute(self, key: str, value: str) -> None:
        self._gui_attributes[key] = value
        self._changed.append('gui_attributes')

    def rmGuiAttribute(self, key: str) -> None:
        if self._gui_attributes.get(key) is not None:
            del self._gui_attributes[key]
            self._changed.append('gui_attributes')

    @property
    def label(self) -> Optional[LangString]:
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
                raise BaseError('Not a valid LangString')
        self._changed.add('label')

    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        self._label[lang] = value
        self._changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        del self._label[lang]
        self._changed.add('label')

    @property
    def comment(self) -> Optional[LangString]:
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
                raise BaseError('Not a valid LangString')
        self._changed.add('comment')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        self._comment[lang] = value
        self._changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self._comment[lang]
        self._changed.add('comment')

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
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> Any:
        if isinstance(json_obj, list):
            json_obj = json_obj[0]  # TODO: Is it possible to have more than one element in the list??
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if not (json_obj.get(knora_api + ':isResourceProperty')):
            raise BaseError("This is not a property!")
        if json_obj.get('@id') is None:
            raise BaseError('Property class has no "@id"!')
        tmp_id = json_obj.get('@id').split(':')
        id = context.iri_from_prefix(tmp_id[0]) + '#' + tmp_id[1]
        ontology_id = tmp_id[0]
        name = tmp_id[1]
        superproperties_obj = json_obj.get(rdfs + ':subPropertyOf')
        superproperties: List[Union[None, str]]
        if not isinstance(superproperties_obj, list):
            superproperties_obj = [superproperties_obj]  # make a list out of it
        if superproperties_obj is not None:
            superprops: List[Any] = list(filter(lambda a: a.get('@id') is not None, superproperties_obj))
            superproperties = list(map(lambda a: a['@id'], superprops))
        else:
            superproperties = None
        object = WithId(json_obj.get(knora_api + ':objectType')).str()
        subject = WithId(json_obj.get(knora_api + ':subjectType')).str()
        label = LangString.fromJsonLdObj(json_obj.get(rdfs + ':label'))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs + ':comment'))
        gui_element = None
        if json_obj.get(salsah_gui + ':guiElement') is not None:
            gui_element = WithId(json_obj.get(salsah_gui + ':guiElement')).str()
        gui_attributes_list = json_obj.get(salsah_gui + ':guiAttribute')
        gui_attributes: Union[None, Dict[str, str]] = None
        if gui_attributes_list is not None:
            gui_attributes = {}
            if not isinstance(gui_attributes_list, list):
                gui_attributes_list = [gui_attributes_list]
            for ga in gui_attributes_list:
                tmp = ga.split('=')
                if len(tmp) == 1:
                    gui_attributes[tmp[0]] = ''
                else:
                    gui_attributes[tmp[0]] = tmp[1]

        editable = json_obj.get(knora_api + ':isEditable')
        linkvalue = json_obj.get(knora_api + ':isLinkProperty')
        return cls(con=con,
                   context=context,
                   id=id,
                   name=name,
                   ontology_id=ontology_id,
                   superproperties=superproperties,
                   object=object,
                   subject=subject,
                   gui_element=gui_element,
                   gui_attributes=gui_attributes,
                   label=label,
                   comment=comment,
                   editable=editable,
                   linkvalue=linkvalue)

    def toJsonObj(self, lastModificationDate: LastModificationDate, action: Actions, what: Optional[str] = None) -> Any:

        def resolve_propref(resref: str):
            tmp = resref.split(':')
            if len(tmp) > 1:
                if tmp[0]:
                    #                    return {"@id": resref}  # fully qualified name in the form "prefix:name"
                    return {"@id": self._context.get_qualified_iri(
                        resref)}  # fully qualified name in the form "prefix:name"
                else:
                    return {"@id": self._context.prefix_from_iri(self._ontology_id) + ':' + tmp[
                        1]}  # ":name" in current ontology
            else:
                return {"@id": "knora-api:" + resref}  # no ":", must be from knora-api!

        tmp = {}
        exp = re.compile('^http.*')  # It is already a fully IRI
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
                "@graph": [{
                    "@id": propid,
                    "@type": "owl:ObjectProperty",
                    "rdfs:label": self._label.toJsonLdObj(),
                    "rdfs:subPropertyOf": superproperties
                }],
                "@context": self._context.toJsonObj()
            }
            if self._comment is not None:
                if not self._comment.isEmpty():
                    tmp['@graph'][0]["rdfs:comment"] = self._comment.toJsonLdObj()
            if self._subject is not None:
                tmp['@graph'][0]["knora-api:subjectType"] = resolve_propref(self._subject)
            if self._object is not None:
                tmp['@graph'][0]["knora-api:objectType"] = resolve_propref(self._object)
            if self._gui_element is not None:
                tmp['@graph'][0]["salsah-gui:guiElement"] = {
                    "@id": self._gui_element
                }
            if self._gui_attributes:
                ga = list(map(lambda x: x[0] + '=' + str(x[1]), self._gui_attributes.items()))
                tmp['@graph'][0]["salsah-gui:guiAttribute"] = ga
        elif action == Actions.Update:
            tmp = {
                "@id": ontid,  # self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": propid,
                    "@type": "owl:ObjectProperty",
                }],
                "@context": self._context.toJsonObj(),
            }
            if what == 'label':
                if not self._label.isEmpty() and 'label' in self._changed:
                    tmp['@graph'][0]['rdfs:label'] = self._label.toJsonLdObj()
            if what == 'comment':
                if not self._comment.isEmpty() and 'comment' in self._changed:
                    tmp['@graph'][0]['rdfs:comment'] = self._comment.toJsonLdObj()

        return tmp

    def create(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'PropertyClass']:
        jsonobj = self.toJsonObj(last_modification_date, Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=2)
        result = self._con.post('/v2/ontologies/properties', jsondata)
        last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
        return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result['@graph'])

    def update(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        #
        # Note: Knora is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if 'label' in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'label')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self._con.put('/v2/ontologies/properties', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if 'comment' in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'comment')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self._con.put('/v2/ontologies/properties', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if something_changed:
            return last_modification_date, PropertyClass.fromJsonObj(self._con, self._context, result['@graph'])
        else:
            return last_modification_date, self

    def delete(self, last_modification_date: LastModificationDate) -> LastModificationDate:
        result = self._con.delete('/v2/ontologies/properties/' + quote_plus(self._id) + '?lastModificationDate=' + str(
            last_modification_date))
        return LastModificationDate(result['knora-api:lastModificationDate'])

    def createDefinitionFileObj(self, context: Context, shortname: str):
        """
        Create an object that jsonfied can be used as input to "create_onto"

        :param context: Context of the ontology
        :param shortname: Shortname of the ontology
        :return: Python object to be jsonfied
        """
        property = {
            "name": self._name
        }
        if self._object is not None:
            property["name"] = self._name
        if self._superproperties is not None:
            superprops = []
            for sc in self._superproperties:
                superprops.append(context.reduce_iri(sc, shortname))
            property["super"] = superprops
        if self._object is not None:
            property["object"] = context.reduce_iri(self._object, shortname)
        if self._label is not None:
            property["labels"] = self._label.createDefinitionFileObj()
        if self._gui_element is not None:
            property["gui_element"] = context.reduce_iri(self._gui_element, shortname)
        if self._gui_attributes:
            gui_elements = {}
            for (attname, attvalue) in self._gui_attributes.items():
                if attname == "size":
                    gui_elements[attname] = int(attvalue)
                elif attname == "maxsize":
                    gui_elements[attname] = int(attvalue)
                elif attname == "hlist":
                    iri = attvalue[1:-1]
                    rootnode = ListNode(con=self._con, id=iri).read()
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
            property["gui_attributes"] = gui_elements
        return property

    def print(self, offset: int = 0):
        blank = ' '
        print(f'{blank:>{offset}}Property Class Info')
        print(f'{blank:>{offset + 2}}Name:            {self._name}')
        print(f'{blank:>{offset + 2}}Ontology prefix: {self._ontology_id}')
        print(f'{blank:>{offset + 2}}Superproperties:')
        if self._superproperties is not None:
            for sc in self._superproperties:
                print(f'{blank:>{offset + 4}}{sc}')
        if self._label is not None:
            print(f'{blank:>{offset + 2}}Labels:')
            self._label.print(offset + 4)
        if self._subject is not None:
            print(f'{blank:>{offset + 4}}Subject: {self._subject}')
        if self._object is not None:
            print(f'{blank:>{offset + 4}}Object: {self._object}')
        if self._gui_element is not None:
            print(f'{blank:>{offset + 4}}Guielement: {self._gui_element}')
        if self._gui_attributes is not None:
            print(f'{blank:>{offset + 4}}Gui Attributes:')
            if self._gui_attributes is not None:
                for (attname, attvalue) in self._gui_attributes.items():
                    print(f'{blank:>{offset + 6}}Attribute: {attname} Value: {attvalue}')
        if self._comment is not None:
            print(f'{blank:>{offset + 2}}Comments:')
            self._comment.print(offset + 4)
        if self._editable is not None:
            print(f'{blank:>{offset + 4}}Editable: {self._editable}')
        if self._linkvalue is not None:
            print(f'{blank:>{offset + 4}}Editable: {self._linkvalue}')
