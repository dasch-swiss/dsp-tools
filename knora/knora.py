from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import quote_plus
from rdflib import Graph
from lxml import etree
import requests
import json
import urllib
import pprint
import validators
import re


# TODO: recheck all the documentation of this file
"""
 Properties in knora-api:

 - :hasValue
 - :hasColor
 - :hasComment
 - :hasGeometry
 - :hasLinkTo
 - :isPartOf
 - :isRegionOf
 - :isAnnotationOf
 - :seqnum

 Classes in knora-api:

 - :Resource
 - :StillImageRepresentation
 - :TextRepresentation
 - :AudioRepresentation
 - :DDDRepresentation
 - :DocumentRepresentation
 - :MovingImageRepresentation
 - :Annotation -> :hasComment, :isAnnotationOf, :isAnnotationOfValue
 - :LinkObj -> :hasComment, :hasLinkTo, :hasLinkToValue
 - :LinkValue [reification node]
 - :Region -> :hasColor, :isRegionOf, :hasGeometry, :isRegionOfValue, :hasComment

 For lists:

 - :ListNode -> :hasSubListNode, :listNodePosition, :listNodeName, :isRootNode, :hasRootNode, :attachedToProject

 Values in knora-api:

 - :Value
 - :TextValue       -> :SimpleText, :TextArea
 - :ColorValue      -> :Colorpicker
 - :DateValue       -> :Date
 - :DecimalValue    -> :SimpleText
 - :GeomValue       -> :Geometry
 - :GeonameValue    -> :Geonames
 - :IntValue        -> :SimpleText, :Spinbox, :Slider
 - :BooleanValue    -> :Checkbox
 - :UriValue        -> :SimpleText
 - :IntervalValue
 - :ListValue       -> :Pulldown

 GUI elements

 - :Colorpicker     -> ncolors=integer
 - :Date
 - :Geometry
 - :Geonames
 - :Interval
 - :List            -> hlist(required)=<iri>
 - :Pulldown        -> hlist(required)=<iri>
 - :Radio           -> hlist(required)=<iri>
 - :Richtext
 - :Searchbox       -> numprops=integer
 - :SimpleText      -> maxlength=integer, size=integer
 - :Slider          -> max(required)=decimal, min(required)=decimal
 - :Spinbox         -> max=decimal, min=decimal
 - :Textarea        -> cols=integer, rows=integer, width=percent, wrap=string(soft|hard)
 - :Checkbox
 - :Fileupload

"""
class KnoraError(Exception):
    """Handles errors happening in this file"""

    def __init__(self, message):
        self.message = message


class knora:
    """
    This is the main class which holds all the methods for communication with the Knora backend.
    """

    def __init__(self, server: str, email: str, password: str, prefixes: Dict[str,str] = None):
        """
        Constructor requiring the server address, the user and password of KNORA
        :param server: Address of the server, e.g http://data.dasch.swiss
        :param email: Email of user, e.g., root@example.com
        :param password: Password of the user, e.g. test
        """
        self.server = server
        self.prefixes = prefixes

        credentials = {
            "email": email,
            "password": password
        }
        jsondata = json.dumps(credentials)

        req = requests.post(
            self.server + '/v2/authentication',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            data=jsondata
        )

        self.on_api_error(req)

        result = req.json()
        self.token = result["token"]

    def __del__(self):
        req = requests.delete(
            self.server + '/v2/authentication',
            headers={'Authorization': 'Bearer ' + self.token}
        )

        result = req.json()
        pprint.pprint(result)


    def on_api_error(self, res):
        """
        Method to check for any API errors
        :param res: The input to check, usually JSON format
        :return: Possible KnoraError that is being raised
        """

        if (res.status_code != 200):
            raise KnoraError("KNORA-ERROR: status code=" + str(res.status_code) + "\nMessage:" + res.text)

        if 'error' in res:
            raise KnoraError("KNORA-ERROR: API error: " + res.error)

    def get_existing_projects(self, full: bool = False):
        """Returns a list of existing projects

        :return: List of existing projects
        """

        req = requests.get(self.server + '/admin/projects',
                           headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        result = req.json()

        if 'projects' not in result:
            raise KnoraError("KNORA-ERROR:\n Request got no projects!")
        else:
            if full:
                return result['projects']
            else:
                return list(map(lambda a: a['id'], result['projects']))

    def get_project(self, shortcode: str) -> dict:
        """Returns project data of given project

        :param shortcode: Shortcode of object
        :return: JSON containing the project information
        """

        url = self.server + '/admin/projects/shortcode/' + shortcode
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)

        result = req.json()

        return result["project"]

    def project_exists(self, proj_iri: str):
        """Checks if a given project exists

        :return: Boolean
        """

        projects = self.get_existing_projects()
        return proj_iri in projects

    def create_project(
            self,
            shortcode: str,
            shortname: str,
            longname: str,
            descriptions: Optional[Dict[str, str]] = None,
            keywords: Optional[List[str]] = None,
            logo: Optional[str] = None) -> str:
        """
        Create a new project

        :param shortcode: Dedicated shortcode of project
        :param shortname: Short name of the project (e.g acronym)
        :param longname: Long name of project
        :param descriptions: Dict of the form {lang: descr, …} for the description of the project [Default: None]
        :param keywords: List of keywords
        :param logo: Link to the project logo [default: None]
        :return: Project IRI
        """

        descriptions = list(map(lambda p: {"language": p[0], "value": p[1]}, descriptions.items()))

        project = {
            "shortname": shortname,
            "shortcode": shortcode,
            "longname": longname,
            "description": descriptions,
            "keywords": keywords,
            "logo": logo,
            "status": True,
            "selfjoin": False
        }

        jsondata = json.dumps(project)

        req = requests.post(self.server + "/admin/projects",
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)

        res = req.json()
        return res["project"]["id"]

    def update_project(
            self,
            shortcode: str,
            shortname: Optional[str] = None,
            longname: Optional[str] = None,
            descriptions: Optional[Dict[str, str]] = None,
            keywords: Optional[List[str]] = None,
            logo: Optional[str] = None) -> str:
        """

        :param shortcode:
        :param shortname:
        :param longname:
        :param descriptions:
        :param keywords:
        :param logo:
        :return:
        """

        descriptions = list(map(lambda p: {"language": p[0], "value": p[1]}, descriptions.items()))

        project = {
            "longname": longname,
            "description": descriptions,
            "keywords": keywords,
            "logo": logo,
            "status": True,
            "selfjoin": False
        }

        jsondata = json.dumps(project)
        url = self.server + '/admin/projects/iri/' + quote_plus("http://rdfh.ch/projects/" + shortcode)

        req = requests.put(url,
                           headers={'Content-Type': 'application/json; charset=UTF-8',
                                    'Authorization': 'Bearer ' + self.token},
                           data=jsondata)
        self.on_api_error(req)

        res = req.json()
        return res['project']['id']

    def get_users(self):
        """
        Get a list of all users

        :return:
        """
        url = self.server + '/admin/users'
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()
        return res['users']

    def get_user(self, user_iri: str):
        """
        Get a list of all users

        :return:
        """
        url = self.server + '/admin/users/' + quote_plus(user_iri)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()
        return res['user']

    def create_user(self,
                    username: str,
                    email: str,
                    givenName: str,
                    familyName: str,
                    password: str,
                    lang: str = "en"):
        """
        Create a new user

        :param username: The username for login purposes (must be unique)
        :param email: The email address of the user
        :param givenName: The given name (surname, "Vorname", ...)
        :param familyName: The family name
        :param password: The password for the user
        :param lang: language code, either "en", "de", "fr", "it" [default: "en"]
        :return: The user ID as IRI
        """

        userinfo = {
            "username": username,
            "email": email,
            "givenName": givenName,
            "familyName": familyName,
            "password": password,
            "status": True,
            "lang": lang,
            "systemAdmin": False
        }

        jsondata = json.dumps(userinfo)
        url = self.server + '/admin/users'

        req = requests.post(url,
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)

        self.on_api_error(req)
        res = req.json()

        return res['user']['id']

    def add_user_to_project(self, user_iri: str, project_iri: str):
        print("USER: " + user_iri)
        print("PROJECT: " + project_iri)
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/project-memberships/' + quote_plus(project_iri)
        print(url)
        req = requests.post(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return None

    def get_existing_ontologies(self):
        """

        :return: Returns the metadata of all existing ontologies on v2/ontologies
        """

        req = requests.get(self.server + '/v2/ontologies/metadata',
                           headers={'Authorization': 'Bearer ' + self.token})
        result = req.json()

        if not '@graph' in result:
            raise KnoraError("KNORA-ERROR:\n Request got no graph!")
        else:
            names = list(map(lambda a: a['@id'], result['@graph']))
            return names

    def get_project_ontologies(self, project_code: str) -> Optional[dict]:
        """

        :param project_code:
        :return:
        """

        proj = quote_plus("http://rdfh.ch/projects/" + project_code)
        req = requests.get(self.server + "/v2/ontologies/metadata/" + proj,
                           headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        result = req.json()

        if '@graph' in result:  # multiple ontologies
            ontos = list(map(lambda a: {
                'iri': a['@id'],
                'label': a['rdfs:label'],
                'moddate': a.get('knora-api:lastModificationDate')
            }, result['@graph']))
            return ontos
        elif '@id' in result:  # single ontology
            return [{
                'iri': result['@id'],
                'label': result['rdfs:label'],
                'moddate': result.get('knora-api:lastModificationDate')
            }]
        else:
            return None

    def ontology_exists(self, onto_iri: str):
        """
        Checks if an ontology exists

        :param onto_iri: The possible ontology iri
        :return: boolean
        """

        ontos = self.get_existing_ontologies()

        return onto_iri in ontos

    def get_ontology_lastmoddate(self, onto_iri: str):
        """
        Retrieves the lastModificationDate of a Ontology

        :param onto_iri: The ontology to retrieve the lastModificationDate from.
        :return: The lastModificationDate if it exists. Else, this method returns a dict with (id, None). If the ontology does not exist, it return None.
        """

        req = requests.get(self.server + '/v2/ontologies/metadata',
                           headers={'Authorization': 'Bearer ' + self.token})
        result = req.json()

        all_ontos = {}

        for onto in result['@graph']:
            if 'knora-api:lastModificationDate' in onto:
                all_ontos.__setitem__(onto['@id'], onto['knora-api:lastModificationDate'])
            else :
                all_ontos.__setitem__(onto['@id'], None)

        return all_ontos[onto_iri]

    def create_ontology(self,
                        onto_name: str,
                        project_iri: str,
                        label: str) -> Dict[str, str]:
        """
        Create a new ontology

        :param onto_name: Name of the omntology
        :param project_iri: IRI of the project
        :param label: A label property for this ontology
        :return: Dict with "onto_iri" and "last_onto_date"
        """
        
        ontology = {
            "knora-api:ontologyName": onto_name,
            "knora-api:attachedToProject": {
                "@id": project_iri
            },
            "rdfs:label": label,
            "@context": {
                "rdfs": 'http://www.w3.org/2000/01/rdf-schema#',
                "knora-api": 'http://api.knora.org/ontology/knora-api/v2#'
            }
        }

        jsondata = json.dumps(ontology)

        req = requests.post(self.server + "/v2/ontologies",
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)

        self.on_api_error(req)

        res = req.json()
        #TODO: return also ontology name
        return {"onto_iri": res['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def delete_ontology(self, onto_iri: str, last_onto_date = None):
        """
        A method to delete an ontology from /v2/ontologies
        
        :param onto_iri: The ontology to delete
        :param last_onto_date: the lastModificationDate of an ontology. None by default
        :return: 
        """"" #TODO: add return documentation
        url = self.server + "/v2/ontologies/" + urllib.parse.quote_plus(onto_iri)
        req = requests.delete(url,
                              params={"lastModificationDate": last_onto_date},
                              headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        res = req.json()
        return req

    def get_ontology_graph(self,
                           shortcode: str,
                           name: str):
        """
        Returns the turtle definition of the ontology.

        :param shortcode: Shortcode of the project
        :param name: Name of the ontology
        :return:
        """
        url = self.server + "/ontology/" + shortcode + "/" + name + "/v2"
        turtle = requests.get(url,
                              headers={"Accept": "text/turtle",
                                       'Authorization': 'Bearer ' + self.token})
        self.on_api_error(turtle)
        return turtle.text

    def create_res_class(self,
                         onto_iri: str,
                         onto_name: str,
                         last_onto_date: str,
                         class_name: str,
                         super_class: List[str],
                         labels: Dict[str, str],
                         comments: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Creates a knora resource class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology
        :param last_onto_date: Last modification date as returned by last call
        :param class_name: Name of the class to be created
        :param super_class: List of super classes
        :param labels: Dict with labels in the form { lang: labeltext }
        :param comments: Dict with comments in the form { lang: commenttext }
        :return: Dict with "class_iri" and "last_onto_date"
        """

        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"@language": p[0], "@value": p[1]}, labels.items()))

        if not comments:
            comments = {"en": "none"}

        #
        # using map and iterable to get the proper format
        #
        comments = list(map(lambda p: {"@language": p[0], "@value": p[1]}, comments.items()))

        res_class = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [{
                "@id": onto_name + ":" + class_name,
                "@type": "owl:Class",
                "rdfs:label": labels,
                "rdfs:comment": comments,
                "rdfs:subClassOf": {
                    "@id": super_class
                }
            }],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                onto_name: onto_iri + "#"
            }
        }

        jsondata = json.dumps(res_class, indent=3, separators=(',', ': '))

        req = requests.post(self.server + "/v2/ontologies/classes",
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)

        res = req.json()
        return {"class_iri": res['@graph'][0]['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def create_property(
            self,
            onto_iri: str,
            onto_name: str,
            last_onto_date: str,
            prop_name: str,
            super_props: List[str],
            labels: Dict[str, str],
            gui_element: str,
            gui_attributes: List[str] = None,
            subject: Optional[str] = None,
            object: Optional[str] = None,
            comments: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Create a Knora property

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the Ontology (prefix)
        :param last_onto_date: Last modification date as returned by last call
        :param prop_name: Name of the property
        :param super_props: List of super-properties
        :param labels: Dict with labels in the form { lang: labeltext }
        :param gui_element: Valid GUI-Element
        :param gui_attributes: Valid GUI-Attributes (or None
        :param subject: Full name (prefix:name) of subject resource class
        :param object: Full name (prefix:name) of object resource class
        :param comments: Dict with comments in the form { lang: commenttext }
        :return: Dict with "prop_iri" and "last_onto_date" keys
        """
        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"@language": p[0], "@value": p[1]}, labels.items()))


        if not comments:
            comments = {"en": "none"}

        #
        # using map and iterable to get the proper format
        #
        comments = list(map(lambda p: {"@language": p[0], "@value": p[1]}, comments.items()))

        additional_context = {}
        for sprop in super_props:
            pp = sprop.split(':')
            if pp[0] != "knora-api":
                additional_context[pp[0]] = self.prefixes[pp[0]]

        #
        # using map and iterable to get the proper format
        #
        super_props = list(map(lambda x: {"@id": x}, super_props))
        if len(super_props) == 1:
            super_props = super_props[0]

        propdata = {
            "@id": onto_name + ":" + prop_name,
            "@type": "owl:ObjectProperty",
            "rdfs:label": labels,
            "rdfs:comment": comments,
            "rdfs:subPropertyOf": super_props,
            "salsah-gui:guiElement": {
                "@id": gui_element
            }
        }
        if subject:
            propdata["knora-api:subjectType"] = {
                "@id": subject
            }

        if object:
            propdata["knora-api:objectType"] = {
                "@id": object
            }

        if gui_attributes:
            propdata["salsah-gui:guiAttribute"] = gui_attributes

        property = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [
                propdata
            ],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                onto_name: onto_iri + "#"
            }
        }
        property["@context"].update(additional_context)
        jsondata = json.dumps(property, indent=3, separators=(',', ': '))

        req = requests.post(self.server + "/v2/ontologies/properties",
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)

        res = req.json()
        return {"prop_iri": res['@graph'][0]['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def create_cardinality(
            self,
            onto_iri: str,
            onto_name: str,
            last_onto_date: str,
            class_iri: str,
            prop_iri: str,
            occurrence: str
    ) -> Dict[str, str]:
        """Add a property with a given cardinality to a class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology (prefix)
        :param last_onto_date: Last modification date as returned by last call
        :param class_iri: IRI of the class to which the property will be added
        :param prop_iri: IRI of the property that should be added
        :param occurrence: Occurrence: "1", "0-1", "0-n" or "1-n"
        :return: Dict with "last_onto_date" key
        """
        switcher = {
            "1": ("owl:cardinality", 1),
            "0-1": ("owl:maxCardinality", 1),
            "0-n": ("owl:minCardinality", 0),
            "1-n": ("owl:minCardinality", 1)
        }
        occurrence = switcher.get(occurrence)
        if not occurrence:
            KnoraError("KNORA-ERROR:\n Invalid occurrence!")

        cardinality = {
            "@id": onto_iri,
            "@type": "owl:Ontology",
            "knora-api:lastModificationDate": last_onto_date,
            "@graph": [{
                "@id": class_iri,
                "@type": "owl:Class",
                "rdfs:subClassOf": {
                    "@type": "owl:Restriction",
                    occurrence[0]: occurrence[1],
                    "owl:onProperty": {
                        "@id": prop_iri
                    }
                }
            }],
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                onto_name: onto_iri + "#"
            }
        }

        jsondata = json.dumps(cardinality, indent=3, separators=(',', ': '))

        req = requests.post(self.server + "/v2/ontologies/cardinalities",
                            headers={'Content-Type': 'application/ld+json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)

        res = req.json()

        return {"last_onto_date": res["knora-api:lastModificationDate"]}

    def create_list_node(self,
                         project_iri: str,
                         labels: Dict[str, str],
                         comments: Optional[Dict[str, str]] = None,
                         name: Optional[str] = None,
                         parent_iri: Optional[str] = None) -> str:
        """
        Creates a new list node. If there is no parent, a root node is created

        :param project_iri: IRI of the project
        :param labels: Dict in the form {lang: label, …} giving the label(s)
        :param comments: Dict in the form {lang: comment, …} giving the comment(s)
        :param name: Name of the list node
        :param parent_iri: None for root node (or omit), otherwise IRI of parent node
        :return: IRI of list node
        """

        #
        # using map and iterable to get the proper format
        #
        labels = list(map(lambda p: {"language": p[0], "value": p[1]}, labels.items()))


        listnode = {
            "projectIri": project_iri,
            "labels": labels,
        }

        #
        # using map and iterable to get the proper format
        #
        if comments is not None:
            listnode["comments"] = list(map(lambda p: {"language": p[0], "value": p[1]}, comments.items()))
        else:
            listnode["comments"] = []

        if name is not None:
            listnode["name"] = name

        if parent_iri is not None:
            listnode["parentNodeIri"] = parent_iri
            url = self.server + "/admin/lists/" + quote_plus(parent_iri)
        else:
            url = self.server + "/admin/lists"

        jsondata = json.dumps(listnode, indent=3, separators=(',', ': '))


        req = requests.post(url,
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)

        res = req.json()

        if parent_iri is not None:
            return res['nodeinfo']['id']
        else:
            return res['list']['listinfo']['id']

    def get_lists(self, shortcode: str):
        """
        Get the lists belonging to a certain project identified by its shortcode
        :param shortcode: Project shortcode

        :return: JSON with the lists
        """
        url = self.server + "/admin/lists?projectIri=" + quote_plus("http://rdfh.ch/projects/" + shortcode)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return req.json()

    def get_complete_list(self, list_iri: str):
        """
        Get all the data (nodes) of a specific list

        :param list_iri: IRI of the list
        :return: JSON containing the list info including all nodes
        """
        url = self.server + "/admin/lists/" + quote_plus(list_iri)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return req.json()

    def list_creator(self, children: List):
        """
        internal Helper function

        :param children:
        :return:
        """
        if len(children) == 0:
            res = list(map(lambda a: {"name": a["name"], "id": a["id"]}, children))
        else:
            res = list(map(lambda a: {"name": a["name"], "id": a["id"], "nodes": self.list_creator(a["children"])}, children))
        return res

    def create_schema(self, shortcode: str, shortname: str):
        """
        This method extracts the ontology from the ontology information it gets from Knora. It
        gets the ontology information as n3-data using the Knora API and concerts into a convenient
        python dict that can be used for further processing. It is required by the bulk import ptrocessing
        routines.

        :param shortcode: Shortcode of the project
        :param shortname: Short name of the ontolopgy
        :return: Dict with a simple description of the ontology
        """
        turtle = self.get_ontology_graph(shortcode, shortname)
        g = Graph()
        g.parse(format='n3', data=turtle)
        sparql="""
        SELECT ?res ?prop ?superprop ?otype ?guiele ?attr ?card ?cardval
        WHERE {
            ?res a owl:Class .
            ?res rdfs:subClassOf ?restriction .
            ?restriction a owl:Restriction .
            ?restriction owl:onProperty ?prop .
            ?restriction ?card ?cardval .
            ?prop a owl:ObjectProperty .
            ?prop knora-api:objectType ?otype .
            ?prop salsah-gui:guiElement ?guiele .
            ?prop rdfs:subPropertyOf ?superprop .
            OPTIONAL { ?prop salsah-gui:guiAttribute ?attr } .
            FILTER(?card = owl:cardinality || ?card = owl:maxCardinality || ?card = owl:minCardinality)
        }
        ORDER BY ?res ?prop
        """
        qres = g.query(sparql)

        resources = {}
        resclass = ''
        propname = ''
        link_otypes = []
        propcnt = 0
        propindex= {}  # we have to keep the order of the properties as given in the ontology....
        for row in qres:
            nresclass = row.res.toPython()
            nresclass = nresclass[nresclass.find('#') + 1:]
            if resclass != nresclass:
                resclass = nresclass
                resources[resclass] = []
                propcnt = 0
            superprop = row.superprop.toPython()
            superprop = superprop[superprop.find('#') + 1:]
            if superprop == 'hasLinkToValue':  # we ignore this one....
                continue
            npropname = row.prop.toPython()
            npropname = npropname[npropname.find('#') + 1:]
            attr = row.attr.toPython() if row.attr is not None else None
            if attr is not None:
                attr = attr.split('=')
            if propname == npropname:
                if attr is not None:
                    propcnt -= 1
                    if resources[resclass][propcnt]["attr"] is not None: # TODO: why is this necessary???
                        resources[resclass][propcnt]["attr"][attr[0]] = attr[1].strip('<>')
                continue
            else:
                propname = npropname
            objtype = row.otype.toPython()
            objtype = objtype[objtype.find('#') + 1:]
            card = row.card.toPython()
            card = card[card.find('#') + 1:]
            guiele = row.guiele.toPython()
            guiele = guiele[guiele.find('#') + 1:]
            resources[resclass].append({
                "propname": propname,
                "otype": objtype,
                "superpro": superprop,
                "guiele": guiele,
                "attr": {attr[0]: attr[1].strip('<>')} if attr is not None else None,
                "card": card,
                "cardval": row.cardval.toPython()
            })
            if superprop == "hasLinkTo":
                link_otypes.append(objtype)
            propindex[propname] = propcnt
            propcnt += 1
        listdata = {}
        lists = self.get_lists(shortcode)
        lists = lists["lists"]
        for list in lists:
            tmp = self.get_complete_list(list["id"])
            clist = tmp["list"]
            listdata[clist["listinfo"]["name"]] = {
                "id": clist["listinfo"]["id"],
                "nodes": self.list_creator(clist["children"])
            }
        schema = {
            "shortcode": shortcode,
            "ontoname": shortname,
            "lists": listdata,
            "resources": resources,
            "link_otypes": link_otypes
        }
        return schema


class BulkImport:
    def __init__(self, schema: Dict):
        self.schema = schema
        self.proj_prefix = 'p' + schema['shortcode'] + '-' + schema["ontoname"]
        self.proj_iri = "http://api.knora.org/ontology/" + schema['shortcode'] + "/" + schema["ontoname"] + "/xml-import/v1#"
        self.xml_prefixes = {
            None: self.proj_iri,
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            self.proj_prefix: self.proj_iri,
            "knoraXmlImport": "http://api.knora.org/ontology/knoraXmlImport/v1#"
        }
        self.root = etree.Element('{http://api.knora.org/ontology/knoraXmlImport/v1#}resources', nsmap=self.xml_prefixes)

    def new_xml_element(self, tag: str, options: Dict = None, value: str = None):
        tagp = tag.split(':')
        if len(tagp) > 1:
            fulltag = '{' + self.xml_prefixes.get(tagp[0]) + '}' + tagp[1]
        else:
            fulltag = tagp[0]
        if options is None:
            ele = etree.Element(fulltag)
        else:
            ele = etree.Element(fulltag, options)
        if value is not None:
            ele.text = value
        return ele


    def write_xml(self, filename: str):
        # print(etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        f = open(filename, "wb")
        f.write(etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        f.close()

    def add_resource(self, resclass: str, id: str, label: str, properties: Dict):
        """

        :param resclass:
        :param id:
        :param label:
        :param properties:
        :return:
        """

        def find_list_node_id(nodename: str, nodes: List):
            """
            Finds a list node ID from the nodename in a (eventually hierarchical) list of nodes

            :param nodename: Name of the node
            :param nodes: List of nodes
            :return: the id of the list node (an IRI)
            """
            for node in nodes:
                if node["name"] == nodename:
                    return node["id"]
                if node.get("nodes") is not None and len(node.get("nodes")) > 0:
                    node_id = find_list_node_id(nodename, node["nodes"])
                    if node_id is not None:
                        return node_id
            return None


        def process_properties(propinfo: Dict, valuestr: any):
            """
            Processes a property in order to generate the approptiate XML for V1 bulk import.

            :param pname: property name
            :param valuestr: value of the property
            :return: Tuple with xml options and processed value: (xmlopt, val)
            """
            switcher = {
                'TextValue': {'knoraType': 'richtext_value'},
                'ColorValue': {'knoraType': 'color_value'},
                'DateValue': {'knoraType': 'date_value'},
                'DecimalValue': {'knoraType': 'decimal_value'},
                'GeomValue': {'knoraType': 'geom_value'},
                'GeonameValue': {'knoraType': 'geoname_value'},
                'IntValue': {'knoraType': 'int_value'},
                'BooleanValue': {'knoraType': 'boolean_value'},
                'UriValue': {'knoraType': 'uri_value'},
                'IntervalValue': {'knoraType': 'interval_value'},
                'ListValue': {'knoraType': 'hlist_value'},
                'LinkValue': {'knoraType': 'link_value'}
            }
            for link_otype in self.schema["link_otypes"]:
                switcher[link_otype] = {'knoraType': 'link_value'}
            xmlopt = switcher.get(propinfo["otype"])
            if xmlopt is None:
                raise KnoraError("Did not find " + propinfo["otype"] + " in switcher!")
            if xmlopt['knoraType'] == 'link_value':
                xmlopt['target'] = str(valuestr)
                if validators.url(str(valuestr)):
                    xmlopt['linkType'] = 'iri'
                else:
                    xmlopt['linkType'] = 'ref'
                value = None
            elif propinfo["otype"] == 'ListValue':
                if validators.url(str(valuestr)):
                    # it's a full IRI identifying the node
                    value = valuestr
                else:
                    # it's only a node name. First let's get the node list from the ontology schema
                    list_id = propinfo["attr"]["hlist"]
                    for listname in self.schema["lists"]:
                        if self.schema["lists"][listname]["id"] == list_id:
                            nodes = self.schema["lists"][listname]["nodes"]
                    value = find_list_node_id(str(valuestr), nodes)
                if value == 'http://rdfh.ch/lists/0808/X6bb-JerQyu5ULruCGEO0w':
                    print("BANG!")
                    exit(0)
            elif propinfo["otype"] == 'DateValue':
                # processing and validating date format
                res = re.match('(GREGORIAN:|JULIAN:)?(\d{4})?(-\d{1,2})?(-\d{1,2})?(:\d{4})?(-\d{1,2})?(-\d{1,2})?', str(valuestr))
                if res is None:
                    raise KnoraError("Invalid date format! " + str(valuestr))
                dp = res.groups()
                calendar = 'GREGORIAN:' if dp[0] is None else dp[0]
                y1 = None if dp[1] is None else int(dp[1].strip('-: '))
                m1 = None if dp[2] is None else int(dp[2].strip('-: '))
                d1 = None if dp[3] is None else int(dp[3].strip('-: '))
                y2 = None if dp[4] is None else int(dp[4].strip('-: '))
                m2 = None if dp[5] is None else int(dp[5].strip('-: '))
                d2 = None if dp[6] is None else int(dp[6].strip('-: '))
                if y1 is None:
                    raise KnoraError("Invalid date format! " + str(valuestr))
                if y2 is not None:
                    date1 = y1*10000;
                    if m1 is not None:
                        date1 += m1*100
                    if d1 is not None:
                        date1 += d1
                    date2 = y2 * 10000;
                    if m2 is not None:
                        date2 += m2 * 100
                    if d1 is not None:
                        date2 += d2
                    if date1 > date2:
                        y1, y2 = y2, y1
                        m1, m2 = m2, m1
                        d1, d2 = d2, d1
                value = calendar + str(y1)
                if m1 is not None:
                    value += f'-{m1:02d}'
                if d1 is not None:
                    value += f'-{d1:02d}'
                if y2 is not None:
                    value += f':{y2:04d}'
                if m2 is not None:
                    value += f'-{m2:02d}'
                if d2 is not None:
                    value += f'-{d2:02d}'
            else:
                value = str(valuestr)
            return xmlopt, value

        if self.schema["resources"].get(resclass) is None:
            raise KnoraError('Resource class is not defined in ontlogy!')
        resnode = self.new_xml_element(self.proj_prefix + ':' + resclass, {'id': str(id)})

        labelnode = self.new_xml_element('knoraXmlImport:label')
        labelnode.text = str(label)
        resnode.append(labelnode)

        for prop_info in self.schema["resources"][resclass]:
            # first we check if the cardinality allows to add this property
            if properties.get(prop_info["propname"]) is None:  # this property-value is missing
                if prop_info["card"] == 'cardinality'\
                        and prop_info["cardval"] == 1:
                    raise KnoraError(resclass + " requires exactly one " + prop_info["propname"] + "-value: none supplied!")
                if prop_info["card"] == 'minCardinality'\
                        and prop_info["cardval"] == 1:
                    raise KnoraError(resclass + " requires at least one " + prop_info["propname"] + "-value: none supplied!")
                continue
            if type(properties[prop_info["propname"]]) is list:
                if len(properties[prop_info["propname"]]) > 1:
                    if prop_info["card"] == 'maxCardinality' \
                            and prop_info["cardval"] == 1:
                        raise KnoraError(resclass + " allows maximal one " + prop_info["propname"] + "-value: several supplied!")
                    if prop_info["card"] == 'cardinality'\
                            and prop_info["cardval"] == 1:
                        raise KnoraError(resclass + " requires exactly one " + prop_info["propname"] + "-value: several supplied!")
                for p in properties[prop_info["propname"]]:
                    xmlopt, value = process_properties(prop_info, p)
                    pnode = self.new_xml_element(self.proj_prefix + ':' + prop_info["propname"], xmlopt, value)
                    resnode.append(pnode)
            else:
                xmlopt, value = process_properties(prop_info, properties[prop_info["propname"]])
                if xmlopt['knoraType'] == 'link_value':
                    pnode = self.new_xml_element(self.proj_prefix + ':' + prop_info["propname"])
                    pnode.append(self.new_xml_element(self.proj_prefix + ':' + prop_info["otype"], xmlopt, value))
                else:
                    pnode = self.new_xml_element(self.proj_prefix + ':' + prop_info["propname"], xmlopt, value)
                resnode.append(pnode)
        self.root.append(resnode)


