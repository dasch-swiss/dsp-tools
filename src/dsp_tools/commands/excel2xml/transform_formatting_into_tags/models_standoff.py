from dataclasses import dataclass


@dataclass
class CellChunk:
    def to_str(self) -> str:
        raise NotImplementedError


@dataclass
class TextChunk(CellChunk):
    text: str

    def to_str(self) -> str:
        return self.text


@dataclass
class Bold(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"<strong>{self.contents.to_str()}</strong>"


@dataclass
class Italic(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"<em>{self.contents.to_str()}</em>"


@dataclass
class Underline(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"<u>{self.contents.to_str()}</u>"


@dataclass
class Subscript(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"<sub>{self.contents.to_str()}</sub>"


@dataclass
class Superscript(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"<sup>{self.contents.to_str()}</sup>"


@dataclass
class Link(CellChunk):
    contents: CellChunk
    link: str

    def to_str(self) -> str:
        return f'<a href="{self.link}">{self.contents.to_str()}</a>'


@dataclass
class Linebreak(CellChunk):
    contents: CellChunk

    def to_str(self) -> str:
        return f"{self.contents.to_str()}<br/>"
