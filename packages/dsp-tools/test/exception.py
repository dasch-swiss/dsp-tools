from dataclasses import dataclass


@dataclass
class TestDependencyNotSuccessfulError(Exception):
    def __init__(self, dependency: str) -> None:
        msg = f"The dependency '{dependency}' for tests was not successful."
        super().__init__(msg)
