from dataclasses import dataclass

from dsp_tools.utils.authentication_client import AuthenticationClient


@dataclass
class ListCreationClient:
    auth: AuthenticationClient

    def create_project(self, payload: dict[str, Any]) -> bool:
        url = f"{self.auth.server}/admin/projects"
        headers = {
            "User-Agent": f"DSP-TOOLS/{version('dsp-tools')}",
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/json",
        }
        logger.debug(f"REQUEST: {json.dumps({'method': 'POST', 'url': url, 'payload': payload})}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        logger.debug(f"RESPONSE {response.status_code}: {response.text}")
        return response.ok
