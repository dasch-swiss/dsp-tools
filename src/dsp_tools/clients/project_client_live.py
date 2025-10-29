from typing import Any
from typing import Protocol
from dataclasses import dataclass
from rdflib import Literal
from dsp_tools.clients.project_client import ProjectInfoClient
from dsp_tools.utils.request_utils import RequestParameters, log_request
@dataclass
class ProjectInfoClientLive(ProjectInfoClient):
    api_url: str

    def get_project_iri(self, shortcode: str) -> str | None:
        url = f"{self.api_url}/admin/projects/shortcode/{shortcode}"
        params = RequestParameters("POST", url, 30)
        log_request(params)
        


