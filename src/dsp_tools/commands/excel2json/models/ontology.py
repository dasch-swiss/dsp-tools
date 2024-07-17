from dataclasses import dataclass
from typing import Any


@dataclass
class Property:
    name: str
    super: list[str]
    object: str
    subject: str | None
    labels: dict[str, str]
    comments: dict[str, str] | None
    gui_element: str
    gui_attributes: dict[str, int | str | float] | None

    def make(self) -> dict[str, Any]:
        prop_dict = {"name": self.name, "super": self.super, "object": self.object}
        if self.subject:
            prop_dict["subject"] = self.subject
        prop_dict["labels"] = self.labels
        if self.comments:
            prop_dict["comments"] = self.comments
        prop_dict["gui_element"] = self.gui_element
        if self.gui_attributes:
            prop_dict["gui_attributes"] = self.gui_attributes
        return prop_dict
