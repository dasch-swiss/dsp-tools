from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExcelSheet:
    excel_name: str
    sheet_name: str
    col_info: Columns
    df: pd.DataFrame


@dataclass
class Columns:
    preferred_lang: str
    list_cols: list[str]
    node_cols: list[ColumnNodes]

    def __post_init__(self) -> None:
        self.node_cols = sorted(self.node_cols, key=lambda x: x.level_num, reverse=True)

    def get_all(self) -> set[str]:
        all_col = self.list_cols
        for c in self.node_cols:
            all_col.extend(c.columns)
        return set(all_col)


@dataclass
class ColumnNodes:
    level_num: int
    columns: list[str]
