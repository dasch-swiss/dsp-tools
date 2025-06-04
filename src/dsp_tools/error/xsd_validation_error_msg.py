from dataclasses import dataclass


@dataclass
class XSDValidationMessage:
    line_number: int
    element: str | None
    attribute: str | None
    message: str
