from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SerialiseProperty:
    property_name: str
    values: Sequence[SerialiseValue]

    def serialise(self) -> dict[str, Any]:
        """Serialise the property and all its values."""
        return {self.property_name: [value.serialise() for value in self.values]}


@dataclass(frozen=True)
class SerialiseValue(ABC):
    """A value to be serialised."""

    value: str
    permissions: str | None
    comment: str | None

    @abstractmethod
    def serialise(self) -> dict[str, Any]:
        """Serialise the value."""

    def _get_optionals(self) -> dict[str, str]:
        optionals = {"knora-api:valueHasComment": self.comment} if self.comment else {}
        if self.permissions:
            optionals["knora-api:hasPermissions"] = self.permissions
        return optionals


class SerialiseColor(SerialiseValue):
    """A ColorValue to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:ColorValue",
            "knora-api:colorValueAsColor": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseDecimal(SerialiseValue):
    """A  to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:DecimalValue",
            "knora-api:decimalValueAsDecimal": {
                "@type": "xsd:decimal",
                "@value": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseGeometry(SerialiseValue):
    """A GeomValue to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:GeomValue",
            "knora-api:geometryValueAsGeometry": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseGeoname(SerialiseValue):
    """A GeonameValue to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:GeonameValue",
            "knora-api:geonameValueAsGeonameCode": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseSimpletext(SerialiseValue):
    """A Simpletext to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:TextValue",
            "knora-api:valueAsString": self.value,
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseRichtext(SerialiseValue):
    """A Richtext to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": self.value,
            "knora-api:textValueHasMapping": {
                "@id": "http://rdfh.ch/standoff/mappings/StandardMapping",
            },
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseTime(SerialiseValue):
    """A TimeValue to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:TimeValue",
            "knora-api:timeValueAsTimeStamp": {
                "@type": "xsd:dateTimeStamp",
                "@value": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised


class SerialiseURI(SerialiseValue):
    """A UriValue to be serialised."""

    def serialise(self) -> dict[str, Any]:
        serialised = {
            "@type": "knora-api:UriValue",
            "knora-api:uriValueAsUri": {
                "@type": "xsd:anyURI",
                "@value": self.value,
            },
        }
        serialised.update(self._get_optionals())
        return serialised
