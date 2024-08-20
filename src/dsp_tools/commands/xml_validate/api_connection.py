from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

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
class ProjectClient:
    """Client handling ontology-related requests to the DSP-API."""

    server: str
    token: str
    shortcode: str
    default_ontology: str
    project_iri: str | None = None

    def __post_init__(self) -> None:
        url = f"/admin/projects/shortcode/{self.shortcode}"
        response = self.get(url, {})
        self.project_iri = response.json()["project"]["id"]

    def get(self, url: str, headers: dict[str, str]) -> requests.Response:
        """Get request"""
        try:
            response = requests.get(f"{self.server}{url}", timeout=10, headers=headers)
            if not response.ok:
                raise InputError(
                    f"Unsuccessful Request\n"
                    f"URL: {url}\n"
                    f"Status code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
            return response
        except ConnectionError:
            raise BaseError(f"ConnectionError:\nRequest: {url}") from None
        except TimeoutError:
            raise BaseError(f"TimeoutError:\nRequest: {url}") from None

    def get_project_ontology(self, ontology_name: str) -> dict[str, Any]:
        """
        Retrieve the default ontology of a project from a server.

        Args:
            ontology_name: ontology name

        Returns:
            The json response
        """
        url = f"/ontology/{self.shortcode}/{ontology_name}/v2"
        response = self.get(url, {"Accept": "application/ld+json"})
        res: dict[str, Any] = response.json()
        return res

    def get_list_iris(self) -> list[str]:
        url = f"/admin/lists?projectIri={quote_plus(self.project_iri)}"
        response = self.get(url, {})
        return [x["id"] for x in response.json()["lists"]]

    def get_one_list(self, list_iri: str) -> dict[str, Any]:
        url = f"/admin/lists/{quote_plus(list_iri)}"
        response = self.get(url, {})
        res: dict[str, Any] = response.json()
        return res
