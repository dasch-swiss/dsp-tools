from dataclasses import dataclass
from typing import Any

import requests

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError


@dataclass
class Authentication:
    server: str
    email: str
    password: str

    def get_token(self) -> str:
        """
        Retrieve a session token and store it as class attribute.

        Args:
            email: email address of the user
            password: password of the user

        Raises:
            UserError: if DSP-API returns no token with the provided user credentials
        """
        try:
            response = requests.get(
                url=f"{self.server}/v2/authentication",
                data={"email": self.email, "password": self.password},
                timeout=10,
            )
        except ConnectionError:
            raise BaseError("ConnectionError during the authentication.")
        except TimeoutError:
            raise BaseError("TimeoutError during the authentication.")
        if not (tnk := response.json().get("token")) and not response.ok:
            raise InputError(
                "Unable to retrieve a token from the server with the provided credentials.\n"
                f"Status Code: {response.status_code}"
            )
        return f"Bearer {tnk}"


@dataclass
class OntologyClient:
    """Client handling ontology-related requests to the DSP-API."""

    server: str
    token: str
    shortcode: str
    default_ontology: str

    def get_project_ontology(self, ontology_name: str) -> dict[str, Any]:
        """
        Retrieve the default ontology of a project from a server.

        Args:
            ontology_name: ontology name

        Returns:
            The json response
        """
        try:
            url = f"{self.server}/ontology/{self.shortcode}/{ontology_name}/v2"
            response = requests.get(url, timeout=10, headers={"Accept": "application/ld+json"})
            if not response.ok:
                raise InputError(f"The ontology request returned a status code: {response.status_code}")
            res: dict[str, Any] = response.json()
            return res
        except ConnectionError:
            raise BaseError(
                f"Ontologies for project {self.shortcode} could not be retrieved from the DSP server"
            ) from None
        except TimeoutError:
            raise BaseError("TimeoutError during the authentication.") from None
