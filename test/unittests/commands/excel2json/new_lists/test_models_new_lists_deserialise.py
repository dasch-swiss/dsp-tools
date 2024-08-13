import pytest

from dsp_tools.commands.excel2json.new_lists.models.deserialise import LangColsDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ListDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import NodeDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import SheetDeserialised
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel


class TestSheetDeserialised:
    def test_good(self, sheet_deserialised_corr: SheetDeserialised) -> None:
        pass

    def test_bad(self, sheet_deserialised_bad: SheetDeserialised) -> None:
        pass


class TestListDeserialised:
    def test_good(self, list_deserialised_corr: ListDeserialised) -> None:
        pass

    def test_bad(self, list_deserialised_bad: ListDeserialised) -> None:
        pass


class TestNodeDeserialised:
    def test_good_comment(self, node_deserialised: NodeDeserialised) -> None:
        assert not node_deserialised._check_comments({"en", "de"})

    def test_good_labels(self, node_deserialised: NodeDeserialised) -> None:
        assert not node_deserialised._check_labels({"en", "de"})

    def test_bad_comment(self, node_deserialised: NodeDeserialised) -> None:
        assert not node_deserialised._check_comments({"en", "de", "fr"})

    def test_bad_labels(self, node_deserialised: NodeDeserialised) -> None:
        assert not node_deserialised._check_labels({"en", "de", "fr"})

    def test_bad_labels_good_comments(self, node_deserialised_wrong_labels: NodeDeserialised) -> None:
        res = node_deserialised_wrong_labels.check({"en", "de", "fr"})
        assert isinstance(res, PositionInExcel)
        assert res.row == 3
        assert res.column == "fr_1"

    def test_check_all_good(self, node_deserialised: NodeDeserialised) -> None:
        assert not node_deserialised.check({"en", "de"})


class TestLangColsDeserialised:
    def test_get_tags(self, first_cols_deserialised: LangColsDeserialised) -> None:
        res = first_cols_deserialised.get_tags()
        assert res == {"en", "de"}

    def test_get_ending(self, first_cols_deserialised: LangColsDeserialised) -> None:
        res = first_cols_deserialised.get_ending()
        assert res == "_1"


if __name__ == "__main__":
    pytest.main([__file__])
