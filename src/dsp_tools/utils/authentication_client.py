from typing import Protocol

# ruff: noqa: D102 (missing docstring in public method)


class AuthenticationClient(Protocol):
    """
    Protocol for a client that can authenticate with a DSP server and returns a token.
    """

    def get_token(self) -> str:
        pass
