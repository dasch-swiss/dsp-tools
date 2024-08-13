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
        positions = []
        if problem := self._check_own_labels():
            positions.append(problem)
        if problem := self._check_own_comments():
            positions.append(problem)
        if problems := self._check_all_labels():
            positions.extend(problems)
        if problems := self._check_all_comments():
            positions.extend(problems)
        return positions

    def _check_all_labels(self) -> list[PositionInExcel] | None:
        pass

    def _check_all_comments(self) -> list[PositionInExcel] | None:
        pass

    def _check_own_labels(self) -> PositionInExcel | None:
        pass

    def _check_own_comments(self) -> PositionInExcel | None:
        pass


@dataclass
class NodeDeserialised:
    node_id: str
    parent_id: str
    excel_row: int
    labels: LangColsDeserialised
    comments: LangColsDeserialised | None = None

    def check_own_labels(self, expected_lang_tags: set[str]) -> PositionInExcel | None:
        pass

    def check_own_comments(self, expected_lang_tags: set[str]) -> PositionInExcel | None:
        pass


@dataclass
class LangColsDeserialised:
    content: dict[str, str]

    def get_tags(self) -> set[str]:
        return {x.split("_")[0] for x in self.content}
