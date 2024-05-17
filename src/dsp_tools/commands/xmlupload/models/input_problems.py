from dataclasses import dataclass


@dataclass(frozen=True)
class IIIFUriProblem:
    """Information about a problem with an IIIF URI."""

    uri: str
    passed_regex: bool
    status_code: int | None = None
    response_text: str | None = None
    thrown_exception: Exception | None = None
