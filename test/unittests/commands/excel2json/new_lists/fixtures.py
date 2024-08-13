import pytest

from dsp_tools.commands.excel2json.new_lists.models.deserialise import LangColsDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ListDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import NodeDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import SheetDeserialised


@pytest.fixture()
def list_cols_deserialised() -> LangColsDeserialised:
    return LangColsDeserialised({"en_list": "english list", "de_list": "deutsche Liste"})


@pytest.fixture()
def first_cols_deserialised() -> LangColsDeserialised:
    return LangColsDeserialised({"en_1": "english1", "de_1": "deutsch1"})


@pytest.fixture()
def second_cols_deserialised() -> LangColsDeserialised:
    return LangColsDeserialised({"en_2": "english2", "de_2": "deutsch2"})


@pytest.fixture()
def comment_cols_deserialised() -> LangColsDeserialised:
    return LangColsDeserialised({"en_comment": "english comment", "de_comment": "deutscher Kommentar"})


@pytest.fixture()
def comment_cols_deserialised_three_langs() -> LangColsDeserialised:
    return LangColsDeserialised(
        {"en_comment": "english comment", "de_comment": "deutscher Kommentar", "fr_comment": "comment french"}
    )


@pytest.fixture()
def node_deserialised_with_comments(
    first_cols_deserialised: LangColsDeserialised, comment_cols_deserialised: LangColsDeserialised
) -> NodeDeserialised:
    return NodeDeserialised(
        node_id="id_1",
        parent_id="list_id",
        excel_row=3,
        labels=first_cols_deserialised,
        comments=comment_cols_deserialised,
    )


@pytest.fixture()
def node_deserialised_no_comments(second_cols_deserialised: LangColsDeserialised) -> NodeDeserialised:
    return NodeDeserialised(
        node_id="id_2",
        parent_id="id_1",
        excel_row=4,
        labels=second_cols_deserialised,
    )


@pytest.fixture()
def node_deserialised_wrong_labels(
    first_cols_deserialised: LangColsDeserialised, comment_cols_deserialised_three_langs: LangColsDeserialised
) -> NodeDeserialised:
    return NodeDeserialised(
        node_id="id_1",
        parent_id="list_id",
        excel_row=3,
        labels=first_cols_deserialised,
        comments=comment_cols_deserialised_three_langs,
    )


@pytest.fixture()
def list_deserialised_corr(
    list_cols_deserialised: LangColsDeserialised,
    node_deserialised_with_comments: NodeDeserialised,
    node_deserialised_no_comments: NodeDeserialised,
) -> ListDeserialised:
    return ListDeserialised(
        list_id="list_id",
        lang_tags={"en", "de"},
        labels=list_cols_deserialised,
        nodes=[node_deserialised_with_comments, node_deserialised_no_comments],
    )


@pytest.fixture()
def sheet_deserialised_corr(list_deserialised_corr: ListDeserialised) -> SheetDeserialised:
    return SheetDeserialised(
        excel_name="excel name", sheet_name="sheet correct", list_deserialised=list_deserialised_corr
    )


@pytest.fixture()
def list_deserialised_bad(
    node_deserialised_with_comments: NodeDeserialised,
    node_deserialised_no_comments: NodeDeserialised,
    list_cols_deserialised: LangColsDeserialised,
) -> ListDeserialised:
    return ListDeserialised(
        list_id="list_id",
        lang_tags={"en", "de", "fr"},
        nodes=[node_deserialised_with_comments, node_deserialised_no_comments],
        labels=list_cols_deserialised,
    )


@pytest.fixture()
def sheet_deserialised_bad(
    list_deserialised_bad: ListDeserialised,
) -> SheetDeserialised:
    return SheetDeserialised(excel_name="excel name", sheet_name="sheet wrong", list_deserialised=list_deserialised_bad)


if __name__ == "__main__":
    pytest.main([__file__])
