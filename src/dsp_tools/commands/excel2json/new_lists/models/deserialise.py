from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExcelSheet:
    excel_name: str
    sheet_name: str
    df: pd.DataFrame


@dataclass
class SheetDeserialised:
    excel_name: str
    sheet_name: str
    lang_tags: set[str]
    list_deserialised: ListDeserialised


@dataclass
class ListDeserialised:
    list_id: str
    excel_row: int
    labels: LangColsDeserialised
    comments: LangColsDeserialised | None


@dataclass
class NodeDeserialised:
    node_id: str
    parent_id: str
    excel_row: int
    labels: LangColsDeserialised
    comments: LangColsDeserialised | None


@dataclass
class LangColsDeserialised:
    content: dict[str, str]
