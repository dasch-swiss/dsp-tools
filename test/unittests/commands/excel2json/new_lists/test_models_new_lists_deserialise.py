import pytest

from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.new_lists.models.deserialise import LangColsDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ListDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import NodeDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import SheetDeserialised
from dsp_tools.commands.excel2json.new_lists.models.input_error import MissingListTranslations


class TestSheetDeserialised:
    def test_good(self, sheet_deserialised_corr: SheetDeserialised) -> None:
        assert not sheet_deserialised_corr.check_all()

    def test_bad(self, sheet_deserialised_bad: SheetDeserialised) -> None:
        res = sheet_deserialised_bad.check_all()
        assert isinstance(res, MissingListTranslations)
        assert res.excel_name == "excel name"
        assert res.sheet == "sheet wrong"
        assert len(res.locations) == 1
        location = res.locations[0]
        assert isinstance(location, PositionInExcel)


class TestListDeserialised:
    def test_good(self, list_deserialised_corr_two_lang: ListDeserialised) -> None:
        assert not list_deserialised_corr_two_lang.check_all()

    def test_bad(self, list_deserialised_one_bad_node: ListDeserialised) -> None:
        res = list_deserialised_one_bad_node.check_all()
        assert len(res) == 1
        location = res[0]
        assert isinstance(location, PositionInExcel)
        assert location.row == 4
        assert location.column == "fr_2"


class TestNodeDeserialised:
    def test_check_all_good(self, node_deserialised_with_comments_two_lang: NodeDeserialised) -> None:
        assert not node_deserialised_with_comments_two_lang.check({"en", "de"})

    def test_bad_labels_good_comments(self, node_deserialised_wrong_labels: NodeDeserialised) -> None:
        res = node_deserialised_wrong_labels.check({"en", "de", "fr"})
        assert len(res) == 1
        positions = res[0]
        assert isinstance(positions, PositionInExcel)
        assert positions.row == 3
        assert positions.column == "fr_1"


class TestLangColsDeserialised:
    def test_get_tags(self, first_cols_deserialised_two_lang: LangColsDeserialised) -> None:
        res = first_cols_deserialised_two_lang.get_tags()
        assert res == {"en", "de"}

    def test_get_ending(self, first_cols_deserialised_two_lang: LangColsDeserialised) -> None:
        res = first_cols_deserialised_two_lang.get_ending()
        assert res == "_1"


if __name__ == "__main__":
    pytest.main([__file__])
