from dsp_tools.utils.authentication_client import AuthenticationClient


class AuthenticationClientMockBase(AuthenticationClient):
    def get_token(self) -> str:
        return "mocked_token"
