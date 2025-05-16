from dsp_tools.clients.authentication_client import AuthenticationClient


class AuthenticationClientMockBase(AuthenticationClient):
    server: str
    email: str
    password: str

    def get_token(self) -> str:
        return "mocked_token"
