from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExcelSheet:
    excel_name: str
    sheet_name: str
    df: pd.DataFrame


@dataclass
class Columns:
    list_cols: ColumnsList
    comment_cols: ColumnsComments
    node_cols: list[ColumnNodes]

    def __post_init__(self) -> None:
        self.node_cols = sorted(self.node_cols, key=lambda x: x.level_num, reverse=True)


@dataclass
class ColumnsList:
    columns: list[str]


@dataclass
class ColumnsComments:
    columns: list[str]


@dataclass
class ColumnNodes:
    level_num: int
    columns: list[str]
