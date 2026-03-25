from dataclasses import dataclass
from typing import Any
from typing import Literal


@dataclass
class DOAPResult:
    value: Literal["public", "private"] | None  # set on successful parse
    error: str | None  # set on failure; explanation of what went wrong

    def __post_init__(self) -> None:
        if (self.value is None) == (self.error is None):
            raise ValueError("Exactly one of value or error must be set")


@dataclass
class DoapCategories:
    class_doaps: list[dict[str, Any]]
    prop_doaps: list[dict[str, Any]]
    has_img_all_classes_doaps: list[dict[str, Any]]
    has_img_specific_class_doaps: list[dict[str, Any]]
