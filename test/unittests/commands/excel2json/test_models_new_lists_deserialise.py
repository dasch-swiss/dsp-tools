import pytest

from dsp_tools.commands.excel2json.new_lists.models.deserialise import LangColsDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ListDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import NodeDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import SheetDeserialised


@pytest.fixture()
def list_cols_deserialised() -> LangColsDeserialised:
    pass


@pytest.fixture()
def first_cols_deserialised() -> LangColsDeserialised:
    pass


@pytest.fixture()
def second_cols_deserialised() -> LangColsDeserialised:
    pass


@pytest.fixture()
def comment_cols_deserialised() -> LangColsDeserialised:
    pass


@pytest.fixture()
def node_deserialised(
    first_cols_deserialised: LangColsDeserialised, comment_cols_deserialised: LangColsDeserialised
) -> NodeDeserialised:
    pass


@pytest.fixture()
def node_deserialised_no_comments(second_cols_deserialised: LangColsDeserialised) -> NodeDeserialised:
    pass


@pytest.fixture()
def list_deserialised_corr(
    node_deserialised: NodeDeserialised, node_deserialised_no_comments: NodeDeserialised
) -> ListDeserialised:
    pass


@pytest.fixture()
def sheet_deserialised_corr(list_deserialised_corr: ListDeserialised) -> SheetDeserialised:
    pass


@pytest.fixture()
def list_deserialised_missing_translation(
    node_deserialised: NodeDeserialised, node_deserialised_no_comments: NodeDeserialised
) -> ListDeserialised:
    pass


@pytest.fixture()
def sheet_deserialised_missing_translation(
    list_deserialised_missing_translation: ListDeserialised,
) -> SheetDeserialised:
    pass


if __name__ == "__main__":
    pytest.main([__file__])
