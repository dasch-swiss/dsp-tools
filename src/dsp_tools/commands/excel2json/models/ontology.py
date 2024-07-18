from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OntoProperty:
    name: str
    super: list[str]
    object: str
    subject: str | None
    labels: LanguageDict
    comments: LanguageDict | None
    gui_element: str
    gui_attributes: GuiAttributes | None

    def serialise(self) -> dict[str, Any]:
        prop_dict: dict[str, Any] = {"name": self.name, "super": self.super, "object": self.object}
        if self.subject:
            prop_dict["subject"] = self.subject
        prop_dict["labels"] = self.labels.serialise()
        if self.comments:
            prop_dict["comments"] = self.comments.serialise()
        prop_dict["gui_element"] = self.gui_element
        if self.gui_attributes:
            prop_dict["gui_attributes"] = self.gui_attributes.serialise()
        return prop_dict


@dataclass
class LanguageDict:
    lang_dict: dict[str, str]

    def serialise(self) -> dict[str, str]:
        return self.lang_dict


@dataclass
class GuiAttributes:
    gui_attributes: dict[str, int | str | float]

    def serialise(self) -> dict[str, int | str | float]:
        return self.gui_attributes
