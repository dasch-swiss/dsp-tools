from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Property:
    name: str
    super: list[str]
    object: str
    subject: str | None
    labels: LanguageDict
    comments: LanguageDict | None
    gui_element: str
    gui_attributes: GuiAttributes | None

    def get(self) -> dict[str, Any]:
        prop_dict = {"name": self.name, "super": self.super, "object": self.object}
        if self.subject:
            prop_dict["subject"] = self.subject
        prop_dict["labels"] = self.labels.get()
        if self.comments:
            prop_dict["comments"] = self.comments.get()
        prop_dict["gui_element"] = self.gui_element
        if self.gui_attributes:
            prop_dict["gui_attributes"] = self.gui_attributes.get()
        return prop_dict


@dataclass
class LanguageDict:
    lang_dict: dict[str, str]

    def get(self) -> Any:
        return self.lang_dict


@dataclass
class GuiAttributes:
    gui_attributes: dict[str, int | str | float]

    def get(self) -> Any:
        return self.gui_attributes
