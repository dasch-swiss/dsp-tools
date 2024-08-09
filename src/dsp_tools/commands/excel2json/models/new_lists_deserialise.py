from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExcelFile:
    filename: str
    sheets: list[ExcelSheet]


@dataclass
class ExcelSheet:
    excel_name: str
    sheet_name: str
    df: pd.DataFrame
