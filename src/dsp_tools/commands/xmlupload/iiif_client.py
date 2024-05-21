from dataclasses import dataclass
from typing import Protocol

import requests

from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


@dataclass(frozen=True)
class IIIFUriValidator(Protocol):
    """Interface (protocol) for communication with external IIIF-servers to do a health check."""

    uri: str
    passed_regex: bool

    def validate(self) -> IIIFUriProblem | None:
        """Check if the IIIF-server is reachable and if not it returns information for the user."""


@dataclass(frozen=True)
class IIIFUriValidatorLive:
    """Client handling communication with external IIIF-servers to do a health check."""

    uri: str
    passed_regex: bool

    def validate(self) -> IIIFUriProblem | None:
        """Check if the IIIF-server is reachable and if not it returns information for the user."""
        response = self._make_network_call()
        if isinstance(response, Exception):
            return IIIFUriProblem(uri=self.uri, passed_regex=self.passed_regex, thrown_exception=response)
        match response.ok, self.passed_regex:
            case True, True:
                return None
            case _, _:
                return IIIFUriProblem(
                    uri=self.uri,
                    passed_regex=self.passed_regex,
                    status_code=response.status_code,
                    response_text=response.text,
                )
        return None

    def _make_network_call(self) -> requests.Response | Exception:
        uri = self._make_info_json_uri()
        try:
            return requests.get(
                url=uri,
                headers={"Content-Type": "application/ld+json"},
                timeout=10,
            )
        except Exception as e:  # noqa: BLE001 (blind-except)
            return e

    def _make_info_json_uri(self) -> str:
        splt = self.uri.split("/")
        if len(splt) < 5:
            info_uri = self.uri.rstrip("/")
        else:
            info_uri = "/".join(splt[:-4])
        return f"{info_uri}/info.json"
