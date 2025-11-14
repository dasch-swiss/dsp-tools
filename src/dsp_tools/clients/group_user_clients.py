from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class GroupClient(Protocol):
    api_url: str
    auth: AuthenticationClient

    def get_all_groups(self) -> list[dict[str, Any]]:
        """Get all the groups on this DSP-Server."""

    def create_new_group(self, group_dict: dict[str, Any]) -> str | None:
        """Create a new group."""


class UserClient(Protocol):
    api_url: str
    auth: AuthenticationClient

    def get_user_iri_by_username(self, username: str) -> str | None:
        """Get a user by its username."""

    def post_new_user(self, user_dict: dict[str, Any]) -> str | None:
        """Create a new user."""

    def add_user_as_project_member(self, user_iri: str, project_iri: str) -> bool:
        """Add an existing user to a project."""

    def add_user_as_project_admin(self, user_iri: str, project_iri: str) -> bool:
        """Add a user as a project admin."""

    def add_user_to_custom_groups(self, user_iri: str, groups: list[str]) -> bool:
        """Add a user to a custom group."""
