from dataclasses import dataclass

import requests

from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


@dataclass(frozen=True)
class IIIFUriValidator:
    """Client handling communication with external IIIF-servers to do a health check."""

    uri: str
    regex_has_passed: bool

    def validate(self) -> IIIFUriProblem | None:
        """Check if the IIIF-server is reachable. If not, it returns information for error message."""
        response = self._make_network_call()
        if isinstance(response, Exception):
            return IIIFUriProblem(
                uri=self.uri,
                regex_has_passed=self.regex_has_passed,
                thrown_exception_name=response.__class__.__name__,
                original_text=str(response),
            )
        match response.ok, self.regex_has_passed:
            case True, True:
                return None
            case _, _:
                return IIIFUriProblem(
                    uri=self.uri,
                    regex_has_passed=self.regex_has_passed,
                    status_code=response.status_code,
                    original_text=response.text,
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
