from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass(frozen=True)
class SerialiseProperty:
    property_name: str
    values: list[SerialiseValue]

    def serialise(self) -> dict[str, Any]:
        """Serialise the property and all its values."""
        return {self.property_name: [value.serialise() for value in self.values]}


class SerialiseValue(Protocol):
    """A value to be serialised."""

    value: str
    permissions: str | None
    comment: str | None

    def serialise(self) -> dict[str, Any]:
        """Serialise the value."""

    def _get_optionals(self) -> dict[str, str]:
        optionals = {"knora-api:valueHasComment": self.comment} if self.comment else {}
        if self.permissions:
            optionals["knora-api:hasPermissions"] = self.permissions
        return optionals


@dataclass(frozen=True)
class SerialiseColor(SerialiseValue):
    """A Color to be serialised."""

    value: str
    permissions: str | None
    comment: str | None

    def serialise(self) -> dict[str, Any]:
        """Serialise the URI value."""

        serialised = {
            "@type": "knora-api:ColorValue",
            "knora-api:colorValueAsColor": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


@dataclass(frozen=True)
class SerialiseURI(SerialiseValue):
    """A URI to be serialised."""

    value: str
    permissions: str | None
    comment: str | None

    def serialise(self) -> dict[str, Any]:
        """Serialise the URI value."""

        serialised = {
            "@type": "knora-api:UriValue",
            "knora-api:uriValueAsUri": {
                "@type": "xsd:anyURI",
                "@value": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised
