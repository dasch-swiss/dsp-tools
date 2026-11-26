import urllib.parse
from typing import Any

import requests

from dsp_tools.cli.args import ServerCredentials

KNORA_ATTACHED_TO_USER = "knora-api:attachedToUser"


def util_get_auth_header(creds: ServerCredentials) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=10).json()["token"]
    return {"Authorization": f"Bearer {token}"}


def util_get_user_iri(email: str, creds: ServerCredentials) -> str:
    response = requests.get(
        f"{creds.server}/admin/users/email/{email}", headers=util_get_auth_header(creds), timeout=10
    ).json()
    user_iri: str = response["user"]["id"]
    return user_iri


def util_get_attached_to_user(resource_iri: str, creds: ServerCredentials) -> str:
    response: dict[str, Any] = requests.get(
        f"{creds.server}/v2/resources/{resource_iri.replace('/', '%2F').replace(':', '%3A')}",
        headers=util_get_auth_header(creds),
        timeout=10,
    ).json()
    attached: str = response[KNORA_ATTACHED_TO_USER]["@id"]
    return attached


def util_get_list_node_name(node_iri: str, creds: ServerCredentials) -> str:
    response: dict[str, Any] = requests.get(
        f"{creds.server}/admin/lists/{urllib.parse.quote_plus(node_iri)}/info", timeout=10
    ).json()
    name: str = response["nodeinfo"]["name"]
    return name
