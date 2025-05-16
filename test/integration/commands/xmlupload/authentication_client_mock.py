from dsp_tools.clients.authentication_client import AuthenticationClient


class AuthenticationClientMockBase(AuthenticationClient):
    user: str
    password: str
    server: str

    def get_token(self) -> str:
        return "mocked_token"
