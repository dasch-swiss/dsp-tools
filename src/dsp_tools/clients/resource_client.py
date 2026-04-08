from typing import Any
from typing import Protocol

from dsp_tools.utils.request_utils import ResponseCodeAndText


class ResourceClient(Protocol):
    server: str

    def post_resource(self, resource_json: dict[str, Any], resource_has_bitstream: bool) -> str | ResponseCodeAndText:
        """
        POST a JSON-LD resource payload to /v2/resources.
        """

    def get_resource(self, resource_iri: str) -> dict[str, Any] | ResponseCodeAndText:
        """
        Get an existing resource from the DSP-API
        """
