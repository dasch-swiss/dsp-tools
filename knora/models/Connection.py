import requests
import json
import urllib
import pprint

from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique
from urllib.parse import quote_plus

class KnoraError(Exception):
    """Handles errors happening in this file"""

    def __init__(self, message):
        self.message = message

class Connection:
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
        pass
        #self.logout()

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

    def post(self, path: str, jsondata: str):
        req = requests.post(self.server + path,
                            headers={'Content-Type': 'application/json; charset=UTF-8',
                                     'Authorization': 'Bearer ' + self.token},
                            data=jsondata)
        self.on_api_error(req)
        result = req.json()
        return result

    def get(self, path: str):
        req = requests.get(self.server + path,
                           headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        result = req.json()
        return result

    def put(self, path: str, jsondata: str):
        req = requests.put(self.server + path,
                           headers={'Content-Type': 'application/json; charset=UTF-8',
                                    'Authorization': 'Bearer ' + self.token},
                           data=jsondata)
        self.on_api_error(req)
        result = req.json()
        return result

    def delete(self, path: str):
        req = requests.delete(self.server + path,
                              headers={'Authorization': 'Bearer ' + self.token})
        self.on_api_error(req)
        result = req.json()
        return result

