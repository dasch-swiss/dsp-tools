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
    nodes_cols: list[ColumnNodes]

    def reverse_sorted_node_cols(self) -> list[ColumnNodes]:
        return sorted(self.nodes_cols, key=lambda x: x.level_num, reverse=True)


@dataclass
class ColumnsList:
    columns: list[str]


@dataclass
class ColumnNodes:
    level_num: int
    columns: list[str]
