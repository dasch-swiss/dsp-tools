from typing import Protocol


class AuthenticationClient(Protocol):
    """
    Protocol for a client that can authenticate with a DSP server and returns a token.
    """

    server: str
    email: str
    password: str

    def get_token(self) -> str:
        pass
