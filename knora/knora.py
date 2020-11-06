from typing import List, Set, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus
from rdflib import Graph
from lxml import etree
import requests
import json
import urllib
import pprint
import validators
import re
from rfc3987 import parse
from pprint import pprint
import sys

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


class KnoraStandoffXml:
    """Used to handle XML strings for standoff markup"""

    iriregexp = re.compile(r'IRI:[^:]*:IRI')

    def __init__(self, xmlstr: str):
        self.xmlstr = xmlstr

    def getXml(self):
        return self.xmlstr

    def findall(self):
        return KnoraStandoffXml.iriregexp.findall(self.xmlstr)

    def replace(self, fromStr: str, toStr: str):
        self.xmlstr.replace(fromStr, toStr)


class KnoraStandoffXmlEncoder(json.JSONEncoder):
    """Classes used as wrapper for knora standoff-XML"""
    def default(self, obj):
        if isinstance(obj, KnoraStandoffXml):
            return obj.getXml()
        return json.JSONEncoder.default(self, obj)


class Knora:
    """
    This is the main class which holds all the methods for communication with the Knora backend.
    """

    def __init__(self, server: str, prefixes: Dict[str, str] = None):
        """
        Constructor requiring the server address, the user and password of KNORA
        :param server: Address of the server, e.g https://api.dasch.swiss
        :param prefixes: Ontology prefixes used
        """
        self.server = server
        self.prefixes = prefixes
        self.token = None

    def login(self, email: str, password: str) -> None:
        """
        Method to login into KNORA which creates a session token.
        :param email: Email of user, e.g., root@example.com
        :param password: Password of the user, e.g. test
        """
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

    def get_token(self) -> str:
        return self.token

    def logout(self) -> None:
        if self.token is not None:
            req = requests.delete(
                self.server + '/v2/authentication',
                headers={'Authorization': 'Bearer ' + self.token}
            )
            self.on_api_error(req)
            self.token = None

    def __del__(self):
        self.logout()

    def on_api_error(self, res) -> None:
        """
        Method to check for any API errors
        :param res: The input to check, usually JSON format
        :return: Possible KnoraError that is being raised
        """

        if (res.status_code != 200):
            raise KnoraError("KNORA-ERROR: status code=" + str(res.status_code) + "\nMessage:" + res.text)

        if 'error' in res:
            raise KnoraError("KNORA-ERROR: API error: " + res.error)

    #==========================================================================
    # project related methods
    #

    def get_existing_projects(self, full: bool = False) -> List[Any]:
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

    def get_project(self, shortcode: str) -> Dict[str,Any]:
        """Returns project data of given project

        :param shortcode: Shortcode of object
        :return: JSON containing the project information
        """

        url = self.server + '/admin/projects/shortcode/' + shortcode
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)

        result = req.json()

        return result["project"]

    def project_exists(self, proj_iri: str) -> bool:
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
            "status": True,
            "selfjoin": False
        }
        if descriptions is not None:
            project['description'] = descriptions
        if keywords is not None:
            project['keywords'] = keywords
        if logo is not None:
            project['logo'] = logo

        jsondata = json.dumps(project)
        # print(jsondata)

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
        Update project information

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

    #==========================================================================
    # Group related methods
    #

    def get_groups(self) -> List[Dict[str,Any]]:
        """
        Returns the list of existing groups

        :return: List of projects
        """
        url = self.server + '/admin/groups'

        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()

        return res['groups']

    def get_group_by_iri(self, group_iri: str) -> Dict[str,Any]:
        """
        Returns information about the given group
        :param group_iri: IRI of the group
        :return: Information about the specific group
        """
        url = self.server + '/admin/groups/' + quote_plus(group_iri)

        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()

        return res['group']

    def get_group_by_pshortname_and_gname(self,
                                          project_shortname: str,
                                          group_name: str) -> Union[str,None]:
        """
        Get a group by project shortname and group name

        :param project_shortname: Project shortname
        :param group_name: Group name
        :return: IRI of the group
        """
        groupinfos = self.get_groups()
        for groupinfo in groupinfos:
            if groupinfo["project"]["shortname"] == project_shortname and groupinfo["name"] == group_name:
                return groupinfo["id"]
        return None

    def get_group_by_pshortcode_and_gname(self,
                                          project_shortcode: str,
                                          group_name: str) -> Union[str, None]:
        """
        Get a group by project shortcode and group name

        :param project_shortname: Project shortcode
        :param group_name: Group name
        :return: IRI of the group
        """
        groupinfos = self.get_groups()
        for groupinfo in groupinfos:
            if groupinfo["project"]["shortcode"] == project_shortcode and groupinfo["name"] == group_name:
                return groupinfo["id"]
        return None

    def get_group_by_piri_and_gname(self,
                                    project_iri: str,
                                    group_name: str) -> Union[str, None]:
        """
        Get a group by project shortcode and group name

        :param project_shortname: Project shortcode
        :param group_name: Group name
        :return: IRI of the group
        """
        groupinfos = self.get_groups()
        for groupinfo in groupinfos:
            if groupinfo["project"]["id"] == project_iri and groupinfo["name"] == group_name:
                return groupinfo["id"]
        return None

    def create_group(self,
                     project_iri: str,
                     name: str,
                     description: Union[str, Dict[str,str]],
                     status: bool = True,
                     selfjoin: bool = False) -> str:
        """
        Create a new group

        :param name: Name of the group
        :param description: Either a string with the descrioption, or a List of Dicts in the form [{"value": "descr", "language": "lang"},…]
        :param project_iri: IRI of the project where the group belongs to
        :param status: Active (True) or not active (False) [default: True]
        :param selfjoin: ?? [default: False]
        :return: IRI of the group
        """

        groupinfo = {
            "name": name,
            "description": description if isinstance(description, str) else list(map(lambda p: {"@language": p[0], "@value": p[1]}, description.items())),
            "project": project_iri,
            "status": status,
            "selfjoin": selfjoin
        }
        jsondata = json.dumps(groupinfo)

        url = self.server + '/admin/groups'

        req = requests.post(url,
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)

        self.on_api_error(req)
        res = req.json()
        return res['group']['id']

    def update_group(self,
                     group_iri: str,
                     name: Optional[str] = None,
                     description: Optional[Union[str, Dict[str,str]]] = None,
                     selfjoin: Optional[bool] = None) -> Union[str,None]:
        """
        Modify the data about a group. Only parameters that have to be changed must be indicated
        :param group_iri: IRI of the grouo to be modified
        :param name: New name of the group [optional]
        :param description: Either a string with the descrioption, or a List of Dicts in the form [{"value": "descr", "language": "lang"},…] [optional]
        :param selfjoin: True or False [optional]
        :return: ???
        """

        groupinfo = {}
        done = False
        if name is not None:
            groupinfo['name'] = name
            done = True
        if description is not None:
            groupinfo['description'] = description if isinstance(description, str) else list(map(lambda p: {"@language": p[0], "@value": p[1]}, description.items()))
            done = True
        if selfjoin is not None:
            groupinfo['selfjoin'] = selfjoin
            done = True
        if done:
            jsondata = json.dumps(groupinfo)

            url = self.server + '/admin/groups/' + quote_plus(group_iri)

            req = requests.put(url,
                                headers={'Content-Type': 'application/json; charset=UTF-8',
                                         'Authorization': 'Bearer ' + self.token},
                                data=jsondata)
            self.on_api_error(req)
            res = req.json()
            pprint(res)
            return res['group']['id']
        else:
            return None

    def change_group_status(self,
                            group_iri: str,
                            status: bool) -> None:
        """
        Change the status of th group

        :param group_iri: IRI of the group
        :param status: Status (active: True, inactive: False)

        :return: None
        """

        statusinfo = {
            "status": status
        }
        jsondata = json.dumps(statusinfo)

        url = self.server + '/admin/groups/' + quote_plus(group_iri) + '/status'

        req = requests.put(url,
                           headers={'Content-Type': 'application/json; charset=UTF-8',
                                    'Authorization': 'Bearer ' + self.token},
                           data=jsondata)
        self.on_api_error(req)
        res = req.json()
        pprint(res)

    def delete_group(self,
                     group_iri: str) -> None:
        """
        Delete a group
        :param group_iri: IRI of the group
        :return:
        """
        url = self.server + '/admin/groups/' + quote_plus(group_iri)

        req = requests.delete(url,
                              headers={'Content-Type': 'application/json; charset=UTF-8',
                                       'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        res = req.json()
        pprint(res)

    #==========================================================================
    #  User related methods
    #

    def get_users(self) -> List[Dict[str,Any]]:
        """
        Get a list of all users

        :return: Json result.
        """
        url = self.server + '/admin/users'
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()
        return res['users']

    def get_user_by_iri(self, user_iri: str):
        """
        Get single user

        :return:
        """
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()
        return res['user']

    def get_user_by_email(self, email: str):
        """
        Get a list of all users

        :return:
        """
        url = self.server + '/admin/users/email/' + quote_plus(email)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})

        self.on_api_error(req)
        res = req.json()
        return res['user']

    def create_user(self,
                    username: str,
                    email: str,
                    given_name: str,
                    family_name: str,
                    password: str,
                    lang: str = "en",
                    sysadmin: bool = False):
        """
        Create a new user

        :param username: The username for login purposes (must be unique)
        :param email: The email address of the user
        :param given_name: The given name (surname, "Vorname", ...)
        :param family_name: The family name
        :param password: The password for the user
        :param lang: language code, either "en", "de", "fr", "it" [default: "en"]
        :param sysadmin: True if the user has system admin rights
        :return: The user ID as IRI
        """

        userinfo = {
            "username": username,
            "email": email,
            "givenName": given_name,
            "familyName": family_name,
            "password": password,
            "status": True,
            "lang": lang,
            "systemAdmin": sysadmin
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

    def update_user(self,
                    user_iri: str,
                    username: Optional[str] = None,
                    email:  Optional[str] = None,
                    given_name: Optional[str] = None,
                    family_name: Optional[str] = None,
                    password: Optional[str] = None,
                    lang: Optional[str] = None):
        userinfo: Dict[str,Any] = {};
        if username is not None:
            userinfo["username"] = username
        if email is not None:
            userinfo["email"] = email
        if given_name is not None:
            userinfo["givenName"] = given_name
        if family_name is not None:
            userinfo["familyName"] = family_name
        #if password is not None:
        #    update_user["password"] = password
        if lang is not None:
            userinfo["lang"] = lang
        if len(userinfo) > 0:
            url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/BasicUserInformation'
            jsondata = json.dumps(userinfo)
            req = requests.put(url,
                               headers={'Content-Type': 'application/json; charset=UTF-8',
                                        'Authorization': 'Bearer ' + self.token},
                               data=jsondata)
            self.on_api_error(req)

    def change_user_password(self,
                             user_iri: str,
                             admin_password: str,
                             new_password: str):
        data = {
            "requesterPassword": admin_password,
            "newPassword": new_password
        }
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/Password'
        jsondata = json.dumps(data)
        req = requests.put(url,
                           headers={'Content-Type': 'application/json; charset=UTF-8',
                                    'Authorization': 'Bearer ' + self.token},
                           data=jsondata)
        self.on_api_error(req)

    def add_user_to_project(self,
                            user_iri: str,
                            project_iri: str):
        """
        Add a user to a project

        :param user_iri: IRI of the user
        :param project_iri: IRI of the project
        :return: None
        """
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/project-memberships/'\
              + quote_plus(project_iri)
        req = requests.post(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)

        return None

    def rm_user_from_project(self,
                            user_iri: str,
                            project_iri: str):
        """
        Remove a user from a project

        :param user_iri: IRI of the user
        :param project_iri: IRI of the project
        :return: None
        """
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/project-memberships/' + quote_plus(
            project_iri)
        req = requests.delete(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)

        return None

    def add_user_to_project_admin(self,
                                  user_iri: str,
                                  project_iri: str) -> None:
        """
        Add a user to the project admin group (knora-admin:ProjectAdmin)

        :param user_iri: IRI of user
        :param project_iri: IRI of project
        :return: None
        """
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/project-admin-memberships/' + quote_plus(
            project_iri)
        req = requests.post(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return None

    def rm_user_from_project_admin(self,
                                  user_iri: str,
                                  project_iri: str) -> None:
        """
        Remove a user from the project admin group
        :param user_iri: IRI of user
        :param project_iri: IRI of project
        :return: None
        """
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/project-admin-memberships/' + quote_plus(
            project_iri)
        req = requests.delete(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return None

    def add_user_to_sysadmin(self, user_iri: str) -> None:
        """
        Add a user to the project admin group (knora-admin:ProjectAdmin)

        :param user_iri: IRI of user
        :param project_iri: IRI of project
        :return: None
        """
        data = {
            "systemAdmin": True
        }
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/SystemAdmin'
        jsondata = json.dumps(data)
        req = requests.put(url, headers={'Content-Type': 'application/json; charset=UTF-8',
                                         'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)
        return None

    def rm_user_from_sysadmin(self, user_iri: str) -> None:
        """
        Remove a user from the system admin group

        :param user_iri: IRI of user
        :param project_iri: IRI of project
        :return: None
        """
        data = {
            "systemAdmin": False
        }
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/SystemAdmin'
        jsondata = json.dumps(data)
        req = requests.put(url, headers={'Content-Type': 'application/json; charset=UTF-8',
                                         'Authorization': 'Bearer ' + self.token},
                              data=jsondata)
        self.on_api_error(req)
        return None

    def add_user_to_group(self,
                          user_iri: str,
                          group_iri: str) -> None:
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/group-memberships/' + quote_plus(group_iri)

        req = requests.post(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return None

    def rm_user_from_group(self,
                          user_iri: str,
                          group_iri: str) -> None:
        url = self.server + '/admin/users/iri/' + quote_plus(user_iri) + '/group-memberships/' + quote_plus(group_iri)

        req = requests.delete(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return None

    #==========================================================================
    # Ontology methods
    #

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
            else:
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
        # TODO: return also ontology name
        return {"onto_iri": res['@id'], "last_onto_date": res['knora-api:lastModificationDate']}

    def delete_ontology(self, onto_iri: str, last_onto_date=None):
        """
        A method to delete an ontology from /v2/ontologies

        :param onto_iri: The ontology to delete
        :param last_onto_date: the lastModificationDate of an ontology. None by default
        :return:
        """""  # TODO: add return documentation
        url = self.server + "/v2/ontologies/" + urllib.parse.quote_plus(onto_iri)
        req = requests.delete(url,
                              params={"lastModificationDate": last_onto_date},
                              headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        res = req.json()
        return res

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
                         comments: Optional[Dict[str, str]] = None,
                         permissions: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Creates a knora resource class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology
        :param last_onto_date: Last modification date as returned by last call
        :param class_name: Name of the class to be created
        :param super_class: List of super classes
        :param labels: Dict with labels in the form { lang: labeltext }
        :param comments: Dict with comments in the form { lang: commenttext }
        :param permissions: Dict with permissions in the form
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
        :param gui_attributes: Valid GUI-Attributes (or None)
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
        occurrence: str,
        gui_order: Optional[int] = None
    ) -> Dict[str, str]:
        """Add a property with a given cardinality to a class

        :param onto_iri: IRI of the ontology
        :param onto_name: Name of the ontology (prefix)
        :param last_onto_date: Last modification date as returned by last call
        :param class_iri: IRI of the class to which the property will be added
        :param prop_iri: IRI of the property that should be added
        :param occurrence: Occurrence: "1", "0-1", "0-n" or "1-n"
        :param gui_order: Ordering of properties in GUI
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
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
                onto_name: onto_iri + "#"
            }
        }
        if gui_order is not None:
            cardinality['@graph'][0]["rdfs:subClassOf"]["salsah-gui:guiOrder"] = int(gui_order)




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

    def get_resource_by_label(self,
                              label: str,
                              res_class: Optional[str] = None,
                              limit_to_project: Optional[str] = None,
                              offset: Optional[int] = None):
        url = self.server + "/v2/searchbylabel/" + label
        option = False
        if res_class is not None:
            url += '?limitToResourceClass=' + quote_plus(res_class)
            option = True
        if limit_to_project is not None:
            if option:
                url += '&limitToProject=' + quote_plus(limit_to_project)
            else:
                url += '?limitToProject=' + quote_plus(limit_to_project)
            option = True;
        if offset is not None:
            if option:
                url += '&offset=' + quote_plus(limit_to_project)
            else:
                url += '&offset=' + quote_plus(limit_to_project)
        req = requests.get(url, headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        return req.json()

    def create_resource(self,
                        schema: Dict,
                        res_class: str,
                        label: str,
                        values: Dict,
                        permissions: Optional[str] = None,
                        stillimage: Optional[str] = None):
        """
        This method creates a new resource (instance of a resource class) with the
        default permissions.

        :param schema: The schema of the ontology as returned by the method "create_schema()"
        :param res_class: The resource class of the resource to be created
        :param label: The "rdfs:label" to be given to the new resource
        :param values: A dict with the property values. It has the form
        { property_name: value, property_name: value,… } or { property_name: [value1, value2,…],… }
        The format of the values depends on the value types. E.g. a calendar date has the form
        "GREGORIAN:CE:1920-03-12:CE:1921:05:21" where all values except the start year are optional.
        :param stillimage: Path to a still image...
        :return: A dict in the form { 'iri': resource_iri, 'ark': ark_id, 'vark': dated_ark_id }
        """

        ontoname = schema["ontoname"]
        props = schema['resources'][res_class]  # this is an array of all properties defined in the ontology

        # we start building the dict that will be transformed into the JSON-LD
        jsondata = {
            '@type': ontoname + ":" + res_class,
            'rdfs:label': label,
            "knora-api:attachedToProject": {
                "@id": schema['proj_iri']
            }
        }

        if permissions is not None:
            jsondata["knora-api:hasPermissions"] = permissions

        if stillimage is not None:
            jsondata["knora-api:hasStillImageFileValue"] = {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": stillimage
            }

        def create_valdict(val):
            """
            Internal function to create the JSON-LD for one value
            :param val: the value
            :return: Dict propared for the JSON-LD for one value

            """

            if type(val) is dict:
                pprint(val)
                comment = val.get('comment')
                permissions = val.get('permissions')
                mapping = val.get('mapping')
                val = val.get('value')
            else:
                comment = None
                permissions = None
                mapping = None

            valdict = {
                '@type': 'knora-api:' + prop["otype"]
            }

            if permissions is not None:
                valdict["knora-api:hasPermissions"] = permissions

            if comment is not None:
                valdict["knora-api:valueHasComment"] = comment

            if prop["otype"] == "TextValue":
                if isinstance(val, KnoraStandoffXml):  # text with XML markup
                    valdict['knora-api:textValueAsXml'] = val  # no conversion to string
                    valdict['knora-api:textValueHasMapping'] = {
                        '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping' if mapping is None else mapping
                    }
                else:  # normal text string without markup
                    valdict['knora-api:valueAsString'] = str(val)
            elif prop["otype"] == "ColorValue":
                #
                # a color value as used in HTML (e.g. "#aaccff"
                #
                res = re.match('^#(?:[0-9a-fA-F]{3}){1,2}$', str(val))
                if res is None:
                    raise KnoraError("Invalid ColorValue format! " + str(val))
                valdict['knora-api:colorValueAsColor'] = str(val)
            elif prop["otype"] == "DateValue":
                #
                # A knora date value
                #
                res = re.match(
                    '(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\d{4})?(-\d{1,2})?(-\d{1,2})?(:CE|:BCE)?(:\d{4})?(-\d{1,2})?(-\d{1,2})?',
                    str(val))
                if res is None:
                    raise KnoraError("Invalid date format! " + str(val))
                dp = res.groups()
                calendar = 'GREGORIAN' if dp[0] is None else dp[0].strip('-: ')
                e1 = 'CE' if dp[1] is None else dp[1].strip('-: ')
                y1 = None if dp[2] is None else int(dp[2].strip('-: '))
                m1 = None if dp[3] is None else int(dp[3].strip('-: '))
                d1 = None if dp[4] is None else int(dp[4].strip('-: '))
                e2 = 'CE' if dp[5] is None else dp[5].strip('-: ')
                y2 = None if dp[6] is None else int(dp[6].strip('-: '))
                m2 = None if dp[7] is None else int(dp[7].strip('-: '))
                d2 = None if dp[8] is None else int(dp[8].strip('-: '))
                if y1 is None:
                    raise KnoraError("Invalid date format! " + str(val))
                if y2 is not None:
                    date1 = y1 * 10000
                    if m1 is not None:
                        date1 += m1 * 100
                    if d1 is not None:
                        date1 += d1
                    date2 = y2 * 10000
                    if m2 is not None:
                        date2 += m2 * 100
                    if d2 is not None:
                        date2 += d2
                    if date1 > date2:
                        y1, y2 = y2, y1
                        m1, m2 = m2, m1
                        d1, d2 = d2, d1
                valdict["knora-api:dateValueHasCalendar"] = calendar
                valdict["knora-api:dateValueHasStartEra"] = e1
                valdict["knora-api:dateValueHasStartYear"] = int(y1)
                if m1 is not None:
                    valdict["knora-api:dateValueHasStartMonth"] = int(m1)
                if d1 is not None:
                    valdict["knora-api:dateValueHasStartDay"] = int(d1)
                valdict["knora-api:dateValueHasEndEra"] = e2
                if y2 is not None:
                    valdict["knora-api:dateValueHasEndYear"] = int(y2)
                else:
                    valdict["knora-api:dateValueHasEndYear"] = int(y1)
                if m2 is not None:
                    valdict["knora-api:dateValueHasEndMonth"] = int(m2)
                if d2 is not None:
                    valdict["knora-api:dateValueHasEndDay"] = int(d2)
            elif prop["otype"] == "DecimalValue":
                #
                # a decimal value
                #
                valdict['knora-api:decimalValueAsDecimal'] = {
                    '@type': 'xsd:decimal',
                    '@value': str(val)
                }
            elif prop["otype"] == "GeomValue":
                #
                # A geometry ID
                #
                valdict['knora-api:geometryValueAsGeometry'] = str(val)
            elif prop["otype"] == "GeonameValue":
                #
                # A geoname ID
                #
                valdict['knora-api:geonameValueAsGeonameCode'] = str(val)
            elif prop["otype"] == "IntValue":
                #
                # an integer value
                #
                valdict['knora-api:intValueAsInt'] = int(val)
            elif prop["otype"] == "BooleanValue":
                #
                # a boolean value
                #
                if type(val) == bool:
                    valdict['knora-api:booleanValueAsBoolean'] = val
                elif type(val) == str:
                    if val.upper() == 'TRUE':
                        valdict['knora-api:booleanValueAsBoolean'] = True
                    elif val.upper() == 'FALSE':
                        valdict['knora-api:booleanValueAsBoolean'] = False
                    else:
                        raise KnoraError("Invalid boolean format! " + str(val))
                elif type(val) == int:
                    if val == 0:
                        valdict['knora-api:booleanValueAsBoolean'] = False
                    else:
                        valdict['knora-api:booleanValueAsBoolean'] = True
            elif prop["otype"] == "UriValue":
                #
                # an URI
                #
                valdict['knora-api:uriValueAsUri'] = {
                    "@type": "xsd:anyURI",
                    "@value": str(val)
                }
            elif prop["otype"] == "TimeValue":
                #
                # an URI
                #
                valdict['knora-api:timeValueAsTime'] = {
                    "@type": "xsd:dateTime",
                    "@value": str(val)
                }
            elif prop["otype"] == "IntervalValue":
                #
                # an interval in the form "1.356:2.456"
                #
                iv = val.split(':')
                valdict["knora-api:intervalValueHasEnd"] = {
                    "@type": "xsd:decimal",
                    "@value": str(iv[0])
                }
                valdict["knora-api:intervalValueHasStart"] = {
                    "@type": "xsd:decimal",
                    "@value": str(iv[1])
                }
            elif prop["otype"] == "ListValue":
                try:
                    iriparts = parse(str(val), rule='IRI')
                    if iriparts['scheme'] == 'http' or iriparts['scheme'] == 'https':
                        valdict['knora-api:listValueAsListNode'] = {
                            '@id': str(val)
                        }
                    else:
                        if iriparts['authority'] is not None:
                            raise KnoraError("Invalid list node: \"" + str(val) + "\" !")
                        listname = iriparts['scheme']
                        nodename = iriparts['path']
                        for node in schema['lists'][listname]['nodes']:
                            found = False
                            if node['name'] == nodename:
                                valdict['knora-api:listValueAsListNode'] = {
                                    '@id': node['id']
                                }
                                found = True
                                break
                        if not found:
                            raise KnoraError("Invalid list node: \"" + str(val) + "\" !")
                except ValueError as err:
                    raise KnoraError("Invalid list node: \"" + str(val) + "\" !")

            elif prop["otype"] == "LinkValue":
                valdict['@type'] = 'knora-api:LinkValue'
                valdict['knora-api:linkValueHasTargetIri'] = {
                    '@id': str(val)
                }
            else:
                if prop['otype'] in schema['link_otypes']:
                    valdict['@type'] = 'knora-api:LinkValue'
                    valdict['knora-api:linkValueHasTargetIri'] = {
                        '@id': str(val)
                    }
                else:
                    raise KnoraError("Invalid otype: " + prop['otype'])

            return valdict

        for key, value in values.items():
            prop = None
            for tmpprop in props:
                if tmpprop['propname'] == key:
                    prop = tmpprop
            if prop is None:
                raise KnoraError("Property " + key + " not known!")

            if prop['otype'] == "LinkValue" or prop['otype'] in schema['link_otypes']:
                nkey = key + "Value"
            else:
                nkey = key
            if type(value) is list:
                valarr = []
                for val in value:
                    valarr.append(create_valdict(val))
                jsondata[ontoname + ':' + nkey] = valarr
            else:
                jsondata[ontoname + ':' + nkey] = create_valdict(value)

            jsondata['@context'] = {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                ontoname: schema['onto_iri'] + '#'
            }

        jsonstr = json.dumps(jsondata, indent=3, separators=(',', ': '), cls=KnoraStandoffXmlEncoder)
        print(jsonstr)
        url = self.server + "/v2/resources"
        req = requests.post(url,
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsonstr)
        self.on_api_error(req)

        res = req.json()

        return {
            'iri': res['@id'],
            'ark': res['knora-api:arkUrl']['@value'],
            'vark': res['knora-api:versionArkUrl']['@value']
        }

    def list_creator(self, children: List):
        """
        internal Helper function

        :param children:
        :return:
        """
        if len(children) == 0:
            res = list(map(lambda a: {"name": a["name"], "id": a["id"]}, children))
        else:
            res = list(
                map(lambda a: {"name": a["name"], "id": a["id"], "nodes": self.list_creator(a["children"])}, children))
        return res

    def create_schema(self, shortcode: str, shortname: str):
        """
        This method extracts the ontology from the ontology information it gets from Knora. It
        gets the ontology information as n3-data using the Knora API and concerts into a convenient
        python dict that can be used for further processing. It is required by the bulk import processing
        routines.

        :param shortcode: Shortcode of the project
        :param shortname: Short name of the ontolopgy
        :return: Dict with a simple description of the ontology
        """
        turtle = self.get_ontology_graph(shortcode, shortname)
        # print(turtle)
        g = Graph()
        g.parse(format='n3', data=turtle)

        # Get project and ontology IRI's
        sparql = """
        SELECT ?onto ?proj
        WHERE {
            ?onto a owl:Ontology .
            ?onto knora-api:attachedToProject ?proj
        }
        """
        qres = g.query(sparql)
        for row in qres:
            proj_iri = row.proj.toPython()  # project IRI
            onto_iri = row.onto.toPython()  # ontology IRI

        sparql = """
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
        propindex = {}  # we have to keep the order of the properties as given in the ontology....
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
                propcnt -= 1

                # process attribute (there might be multiple attributes)
                if attr is not None:
                    if resources[resclass][propcnt]["attr"] is not None:  # TODO: why is this necessary???
                        resources[resclass][propcnt]["attr"][attr[0]] = attr[1].strip('<>')

                # process superprop (there might be multiple superprops)
                if superprop not in resources[resclass][propcnt]["superprop"]:
                    resources[resclass][propcnt]["superprop"].append(superprop)
                # pprint.pprint(resources[resclass])
                propcnt += 1
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
                "superprop": [superprop],
                "guiele": guiele,
                "attr": {attr[0]: attr[1].strip('<>')} if attr is not None else None,
                "card": card,
                "cardval": row.cardval.toPython()
            })
            # pprint.pprint(resources[resclass])
            if superprop == "hasLinkTo":
                link_otypes.append(objtype)
            propindex[propname] = propcnt
            propcnt += 1

        # Get info about lists attached to the project
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
            "proj_iri": proj_iri,
            "shortcode": shortcode,
            "ontoname": shortname,
            "onto_iri": onto_iri,
            "lists": listdata,
            "resources": resources,
            "link_otypes": link_otypes
        }
        return schema

    def reset_triplestore_content(self):
        rdfdata = [
            {
                "path": "./knora-ontologies/knora-admin.ttl",
                "name": "http://www.knora.org/ontology/knora-admin"
            },
            {
                "path": "./knora-ontologies/knora-base.ttl",
                "name": "http://www.knora.org/ontology/knora-base"
            },
            {
                "path": "./knora-ontologies/standoff-onto.ttl",
                "name": "http://www.knora.org/ontology/standoff"
            },
            {
                "path": "./knora-ontologies/standoff-data.ttl",
                "name": "http://www.knora.org/data/standoff"
            },
            {
                "path": "./knora-ontologies/salsah-gui.ttl",
                "name": "http://www.knora.org/ontology/salsah-gui"
            },
            {
                "path": "./_test_data/all_data/admin-data.ttl",
                "name": "http://www.knora.org/data/admin"
            },
            {
                "path": "./_test_data/all_data/permissions-data.ttl",
                "name": "http://www.knora.org/data/permissions"
            },
            {
                "path": "./_test_data/all_data/system-data.ttl",
                "name": "http://www.knora.org/data/0000/SystemProject"
            }
        ]
        jsondata = json.dumps(rdfdata)
        url = self.server + '/admin/store/ResetTriplestoreContent?prependdefaults=false'

        req = requests.post(url,
                            headers={'Content-Type': 'application/json; charset=UTF-8'},
                            data=jsondata)
        self.on_api_error(req)
        res = req.json()
        #  pprint(res)
        return res


class Sipi:
    def __init__(self, sipiserver: str, token: str):
        self.sipiserver = sipiserver
        self.token = token

    def on_api_error(self, res):
        """
        Method to check for any API errors
        :param res: The input to check, usually JSON format
        :return: Possible KnoraError that is being raised
        """

        if (res.status_code != 200):
            raise KnoraError("SIPI-ERROR: status code=" + str(res.status_code) + "\nMessage:" + res.text)

        if 'error' in res:
            raise KnoraError("SIPI-ERROR: API error: " + res.error)

    def upload_image(self, filepath):
        files = {
            'file': (filepath, open(filepath, 'rb')),
        }
        req = requests.post(self.sipiserver + "/upload?token=" + self.token,
                            files=files)
        self.on_api_error(req)
        res = req.json()
        return res


class BulkImport:
    def __init__(self, schema: Dict):
        self.schema = schema
        self.proj_prefix = 'p' + schema['shortcode'] + '-' + schema["ontoname"]
        self.proj_iri = "http://api.knora.org/ontology/" + schema['shortcode'] + "/" + schema[
            "ontoname"] + "/xml-import/v1#"
        self.xml_prefixes = {
            None: self.proj_iri,
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            self.proj_prefix: self.proj_iri,
            "knoraXmlImport": "http://api.knora.org/ontology/knoraXmlImport/v1#"
        }
        self.root = etree.Element('{http://api.knora.org/ontology/knoraXmlImport/v1#}resources',
                                  nsmap=self.xml_prefixes)
        self.project_shortcode = schema["shortcode"]

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

    def get_xml_string(self):
        """
        This method returns the Bulk-Import XML as an UTF-8 encoded string.
        :return: UTF-8 encoded string.
        """
        string = etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8')
        return string

    def upload(self, user, password, hostname, port):
        """
        Upload the Bulk-Import XML to the server.
        :param user: the email of the user
        :param password: the password of the user
        :param hostname: the hostname (e.g., localhost, api.example.org, etc.)
        :param port: the port where the API is running (e.g., 3333)
        :return: the JSON response
        """
        project_iri = "http://rdfh.ch/projects/" + self.project_shortcode
        url_encoded_project_iri = urllib.parse.quote_plus(project_iri)
        bulkimport_api_url = "http://" + hostname + ":" + port + "/v1/resources/xmlimport/" + url_encoded_project_iri
        headers = {"Content-Type": "application/xml"}
        r = requests.post(bulkimport_api_url, data=self.get_xml_string(), headers=headers, auth=(user, password))
        return r.json()

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
                # if value == 'http://rdfh.ch/lists/0808/X6bb-JerQyu5ULruCGEO0w':
                #     print("BANG!")
                #     exit(0)
            elif propinfo["otype"] == 'DateValue':
                # processing and validating date format
                res = re.match('(GREGORIAN:|JULIAN:)?(\d{4})?(-\d{1,2})?(-\d{1,2})?(:\d{4})?(-\d{1,2})?(-\d{1,2})?',
                               str(valuestr))
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
                    date1 = y1 * 10000;
                    if m1 is not None:
                        date1 += m1 * 100
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
            raise KnoraError('Resource class is not defined in ontology!')
        resnode = self.new_xml_element(self.proj_prefix + ':' + resclass, {'id': str(id)})

        labelnode = self.new_xml_element('knoraXmlImport:label')
        labelnode.text = str(label)
        resnode.append(labelnode)

        for prop_info in self.schema["resources"][resclass]:
            # first we check if the cardinality allows to add this property
            if properties.get(prop_info["propname"]) is None:  # this property-value is missing
                if prop_info["card"] == 'cardinality' \
                    and prop_info["cardval"] == 1:
                    raise KnoraError(
                        resclass + " requires exactly one " + prop_info["propname"] + "-value: none supplied!")
                if prop_info["card"] == 'minCardinality' \
                    and prop_info["cardval"] == 1:
                    raise KnoraError(
                        resclass + " requires at least one " + prop_info["propname"] + "-value: none supplied!")
                continue
            if type(properties[prop_info["propname"]]) is list:
                if len(properties[prop_info["propname"]]) > 1:
                    if prop_info["card"] == 'maxCardinality' \
                        and prop_info["cardval"] == 1:
                        raise KnoraError(
                            resclass + " allows maximal one " + prop_info["propname"] + "-value: several supplied!")
                    if prop_info["card"] == 'cardinality' \
                        and prop_info["cardval"] == 1:
                        raise KnoraError(
                            resclass + " requires exactly one " + prop_info["propname"] + "-value: several supplied!")
                for p in properties[prop_info["propname"]]:
                    xmlopt, value = process_properties(prop_info, p)
                    if xmlopt['knoraType'] == 'link_value':
                        pnode = self.new_xml_element(self.proj_prefix + ':' + prop_info["propname"])
                        pnode.append(self.new_xml_element(self.proj_prefix + ':' + prop_info["otype"], xmlopt, value))
                    else:
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


class IrisLookup:
    def __init__(self, local_id_to_iri_json):
        self.iris = local_id_to_iri_json

    def get_resource_iri(self, local_id):
        """
        Given the result of the bulk-import as json, allow retrieving the resource
        IRI based on the local ID.
        {'createdResources': [{'clientResourceID': 'LM_1',
                               'label': '1',
                               'resourceIri': 'http://rdfh.ch/0807/rNxoIK-oR_i0-lO21Y9-CQ'},
                              {'clientResourceID': 'LM_2']}

        :param local_id: the local id. resulting JSON from a bulk import upload.
        :return:
        """

        try:
            resources = self.iris["createdResources"]
            iri = ""
            for resource in resources:
                try:
                    res_id = resource["clientResourceID"]
                    if res_id == local_id:
                        iri = resource["resourceIri"]
                    else:
                        pass
                except KeyError:
                    pass

            if iri == "":
                return None
            else:
                return iri
        except KeyError:
            print("IrisLookup.get_resource_iri - 'createdResources' not found")

    def get_iris_json(self):
        return self.iris


class ListsLookup:
    def __init__(self, lists_json):
        self.lists = lists_json

    def get_list_iri(self, listname):
        return self.lists[listname]["id"]

    def get_list_node_iri(self, listname, nodename):
        if nodename is not None:
            nodes = self.lists[listname]["nodes"]
            res = ""
            for node in nodes:
                try:
                    res = node[nodename]["id"]
                except KeyError:
                    pass

            if res == "":
                return None
            else:
                return res
        else:
            return None

    def get_lists_json(self):
        return self.lists


if __name__ == '__main__':
    con = Knora('http://localhost:3333')
    con.login('root@example.com', 'test')
    res = con.get_resource_by_label('Bertschy, Leon',
                                    res_class="http://0.0.0.0:3333/ontology/0807/mls/v2#Lemma")
    print('RES-IRI: ', res['@id'])
    con.logout()

