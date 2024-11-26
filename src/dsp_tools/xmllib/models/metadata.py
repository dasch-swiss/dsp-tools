from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class Metadata:
    copyright_attribution: list[CopyrightAttribution] = field(default_factory=list)
    license: list[CopyrightAttribution] = field(default_factory=list)

    @staticmethod
    def create_new() -> Metadata:
        return Metadata()

    def add_copyright_attribution(self, id_: str, text: str) -> Metadata:
        self.copyright_attribution.append(CopyrightAttribution(id_, text))
        return self

    def add_copyright_from_dict(self, copyright_dict: dict[str, str]) -> Metadata:
        copyright_list = [CopyrightAttribution(k, v) for k, v in copyright_dict.items()]
        self.copyright_attribution.extend(copyright_list)
        return self


@dataclass
class CopyrightAttribution:
    id_: str
    text: str

    @staticmethod
    def create_new(id_: str, text: str) -> CopyrightAttribution:
        pass


@dataclass
class License:
    id_: str
    text: str
    uri: str | None

    @staticmethod
    def create_new(id_: str, text: str, uri: str | None = None) -> License:
        pass
