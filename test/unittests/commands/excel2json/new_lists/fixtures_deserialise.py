import pytest

from dsp_tools.commands.excel2json.new_lists.models.deserialise import LangColsDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ListDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import NodeDeserialised
from dsp_tools.commands.excel2json.new_lists.models.deserialise import SheetDeserialised


@pytest.fixture()
def list_cols_deserialised_two_lang() -> LangColsDeserialised:
    return LangColsDeserialised({"en_list": "english list", "de_list": "deutsche Liste"})


@pytest.fixture()
def first_cols_deserialised_two_lang() -> LangColsDeserialised:
    return LangColsDeserialised({"en_1": "english1", "de_1": "deutsch1"})


@pytest.fixture()
def second_cols_deserialised_two_lang() -> LangColsDeserialised:
    return LangColsDeserialised({"en_2": "english2", "de_2": "deutsch2"})


@pytest.fixture()
def list_cols_deserialised_three_lang() -> LangColsDeserialised:
    return LangColsDeserialised({"en_list": "english list", "de_list": "deutsche Liste", "fr_list": "french list"})


@pytest.fixture()
def second_cols_deserialised_three_lang() -> LangColsDeserialised:
    return LangColsDeserialised({"en_2": "english2", "de_2": "deutsch2", "fr_2": "french2"})


@pytest.fixture()
def node_deserialised_with_comments_two_lang(
    first_cols_deserialised_two_lang: LangColsDeserialised,
) -> NodeDeserialised:
    return NodeDeserialised(
        excel_row=3,
        labels=first_cols_deserialised_two_lang,
    )


@pytest.fixture()
def node_deserialised_no_comments_two_lang(second_cols_deserialised_two_lang: LangColsDeserialised) -> NodeDeserialised:
    return NodeDeserialised(
        excel_row=4,
        labels=second_cols_deserialised_two_lang,
    )


@pytest.fixture()
def node_deserialised_no_comments_three_lang(
    second_cols_deserialised_three_lang: LangColsDeserialised,
) -> NodeDeserialised:
    return NodeDeserialised(
        excel_row=4,
        labels=second_cols_deserialised_three_lang,
    )


@pytest.fixture()
def node_deserialised_wrong_labels(first_cols_deserialised_two_lang: LangColsDeserialised) -> NodeDeserialised:
    return NodeDeserialised(
        excel_row=3,
        labels=first_cols_deserialised_two_lang,
    )


@pytest.fixture()
def list_deserialised_corr_two_lang(
    node_deserialised_with_comments_two_lang: NodeDeserialised,
    node_deserialised_no_comments_two_lang: NodeDeserialised,
) -> ListDeserialised:
    return ListDeserialised(
        lang_tags={"en", "de"},
        nodes=[node_deserialised_with_comments_two_lang, node_deserialised_no_comments_two_lang],
    )


@pytest.fixture()
def sheet_deserialised_corr(list_deserialised_corr_two_lang: ListDeserialised) -> SheetDeserialised:
    return SheetDeserialised(
        excel_name="excel name", sheet_name="sheet correct", list_deserialised=list_deserialised_corr_two_lang
    )


@pytest.fixture()
def list_deserialised_one_bad_node(
    node_deserialised_no_comments_three_lang: NodeDeserialised,
    node_deserialised_no_comments_two_lang: NodeDeserialised,
) -> ListDeserialised:
    return ListDeserialised(
        lang_tags={"en", "de", "fr"},
        nodes=[node_deserialised_no_comments_three_lang, node_deserialised_no_comments_two_lang],
    )


@pytest.fixture()
def sheet_deserialised_bad(
    list_deserialised_one_bad_node: ListDeserialised,
) -> SheetDeserialised:
    return SheetDeserialised(
        excel_name="excel name", sheet_name="sheet wrong", list_deserialised=list_deserialised_one_bad_node
    )
