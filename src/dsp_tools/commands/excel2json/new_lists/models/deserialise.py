from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.new_lists.models.input_error import MissingListTranslations


@dataclass
class ExcelSheet:
    excel_name: str
    sheet_name: str
    df: pd.DataFrame


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


@dataclass
class SheetDeserialised:
    excel_name: str
    sheet_name: str
    list_deserialised: ListDeserialised

    def check_all(self) -> MissingListTranslations | None:
        if problem := self.list_deserialised.check_all():
            return MissingListTranslations(excel_name=self.excel_name, sheet=self.sheet_name, locations=problem)
        return None


@dataclass
class ListDeserialised:
    list_id: str
    lang_tags: set[str]
    labels: LangColsDeserialised
    nodes: list[NodeDeserialised]
    comments: LangColsDeserialised | None = None

    def check_all(self) -> list[PositionInExcel]:
        positions = self._check_self()
        positions.extend(self._check_all_nodes())
        return positions

    def _check_self(self) -> list[PositionInExcel]:
        problems = _get_missing_columns(self.labels, self.lang_tags, 2)
        if self.comments:
            problems.extend(_get_missing_columns(self.comments, self.lang_tags, 2))
        return problems

    def _check_all_nodes(self) -> list[PositionInExcel]:
        problems = []
        for nd in self.nodes:
            problems.extend(nd.check(self.lang_tags))
        return problems


@dataclass
class NodeDeserialised:
    node_id: str
    parent_id: str
    excel_row: int
    labels: LangColsDeserialised
    comments: LangColsDeserialised | None = None

    def check(self, expected_lang_tags: set[str]) -> list[PositionInExcel]:
        problems = _get_missing_columns(self.labels, expected_lang_tags, self.excel_row)
        if self.comments:
            problems.extend(_get_missing_columns(self.comments, expected_lang_tags, self.excel_row))
        return problems


@dataclass
class LangColsDeserialised:
    content: dict[str, str]

    def get_tags(self) -> set[str]:
        return {x.split("_")[0] for x in self.content}

    def get_ending(self) -> str:
        if len(self.content) == 0:
            return ""
        ending = next(iter(self.content.keys()))
        return f'_{ending.split("_")[1]}'


def _get_missing_columns(
    lang_cols: LangColsDeserialised, expected_lang_tags: set[str], excel_row: int
) -> list[PositionInExcel]:
    if not (label_langs := lang_cols.get_tags()) == expected_lang_tags:
        missing = expected_lang_tags - label_langs
        ending = lang_cols.get_ending()
        return [PositionInExcel(row=excel_row, column=f"{x}{ending}") for x in missing]
    return []
