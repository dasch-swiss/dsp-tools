from typing import Any

from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedUser


def serialise_one_group(group: ParsedGroup, project_iri: str) -> dict[str, Any]:
    return {
        "name": group.name,
        "descriptions": [{"value": desc.text, "language": desc.lang} for desc in group.descriptions],
        "project": project_iri,
        "status": True,
        "selfjoin": False,
    }


def serialise_one_user_for_creation(user: ParsedUser) -> dict[str, Any]:
    return {
        "username": user.username,
        "email": user.email,
        "givenName": user.given_name,
        "familyName": user.family_name,
        "password": user.password,
        "lang": user.lang,
        "status": True,
        "systemAdmin": False,
    }
