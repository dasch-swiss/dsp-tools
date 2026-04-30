from dataclasses import dataclass
from typing import Any


@dataclass
class DoapCategories:
    class_doaps: list[dict[str, Any]]
    prop_doaps: list[dict[str, Any]]
    limited_view_all_classes_doaps: list[dict[str, Any]]
    limited_view_specific_class_doaps: list[dict[str, Any]]
