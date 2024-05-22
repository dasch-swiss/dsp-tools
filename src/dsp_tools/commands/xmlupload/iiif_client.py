from dataclasses import dataclass

import requests

from dsp_tools.commands.xmlupload.models.input_problems import AllIIIFUriProblems
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem
from dsp_tools.utils.uri_util import is_iiif_uri


@dataclass(frozen=True)
class IIIFUriValidator:
    """Client handling communication with external IIIF-servers to do a health check."""

    uri_list: list[str]

    def validate(self) -> AllIIIFUriProblems | None:
        """Validate the URI and return a list of problems if any."""
        iiif_uri_problems = [res for uri in self.uri_list if (res := self._validate_one_uri(uri)) is not None]
        if iiif_uri_problems:
            return AllIIIFUriProblems(problems=iiif_uri_problems)
        return None

    def _validate_one_uri(self, uri: str) -> IIIFUriProblem | None:
        """Check if the IIIF-server is reachable. If not, it returns information for error message."""
        regex_has_passed = is_iiif_uri(uri)
        response = self._make_network_call(uri)
        if isinstance(response, Exception):
            return IIIFUriProblem(
                uri=uri,
                regex_has_passed=regex_has_passed,
                raised_exception_name=response.__class__.__name__,
                original_text=str(response),
            )
        match response.ok, regex_has_passed:
            case True, True:
                return None
            case _:
                return IIIFUriProblem(
                    uri=uri,
                    regex_has_passed=regex_has_passed,
                    status_code=response.status_code,
                    original_text=response.text,
                )

    def _make_network_call(self, uri: str) -> requests.Response | Exception:
        info_json_uri = self._make_info_json_uri(uri)
        try:
            return requests.get(
                url=info_json_uri,
                headers={"Content-Type": "application/ld+json"},
                timeout=10,
            )
        except Exception as e:  # noqa: BLE001 (blind-except)
            return e

    def _make_info_json_uri(self, uri: str) -> str:
        splt = uri.split("/")
        if len(splt) < 5:
            info_uri = uri.rstrip("/")
        else:
            info_uri = "/".join(splt[:-4])
        return f"{info_uri}/info.json"
