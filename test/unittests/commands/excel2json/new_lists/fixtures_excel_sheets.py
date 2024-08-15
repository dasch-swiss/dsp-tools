import pandas as pd
import pytest

from dsp_tools.commands.excel2json.new_lists.models.deserialise import ExcelSheet


@pytest.fixture()
def f1_s1_good_en() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "id (optional)": [11, 22, pd.NA, 44],
            "en_list": ["list1", "list1", "list1", "list1"],
            "en_1": [pd.NA, "node1", "node2", "node3"],
        }
    )
    return ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df)


@pytest.fixture()
def f2_s2_good_en_de() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "id (optional)": [1, 2, pd.NA, 4, 5, 6, 7, pd.NA],
            "en_list": ["list2", "list2", "list2", "list2", "list2", "list2", "list2", "list2"],
            "de_list": ["list2", "list2", "list2", "list2", "list2", "list2", "list2", "list2"],
            "en_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
            "de_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
            "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
            "de_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
            "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
            "de_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )
    return ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df)


@pytest.fixture()
def f1_s1_good_id_filled() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
            "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
            "en_list": [
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
            ],
            "de_list": [
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
            ],
            "en_1": [
                pd.NA,
                "Node_en_1",
                "Node_en_1",
                "Node_en_2",
                "Node_en_3",
                "Node_en_3",
                "Node_en_3",
                "Node_en_3",
                "Node_en_3",
            ],
            "de_1": [
                pd.NA,
                "Node_de_1",
                "Node_de_1",
                "Node_de_2",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
            ],
            "en_2": [
                pd.NA,
                pd.NA,
                "Node_en_1.1",
                pd.NA,
                pd.NA,
                "Node_en_3.1",
                "Node_en_3.2",
                "Node_en_3.2",
                "Node_en_3.2",
            ],
            "de_2": [
                pd.NA,
                pd.NA,
                "Node_de_1.1",
                pd.NA,
                pd.NA,
                "Node_de_3.1",
                "Node_de_3.2",
                "Node_de_3.2",
                "Node_de_3.2",
            ],
            "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_en_3.2.1", "Node_en_3.2.2"],
            "de_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_de_3.2.1", "Node_de_3.2.2"],
        }
    )
    return ExcelSheet(excel_name="excel1", sheet_name="sheet1", df=df)


@pytest.fixture()
def f1_s1_missing_translation_id_filled() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
            "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
            "en_list": [
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                "Listname_en",
                pd.NA,
                "Listname_en",
                "Listname_en",
                "Listname_en",
            ],
            "de_list": [
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
                "Listname_de",
            ],
            "en_1": [
                pd.NA,
                "Node_en_1",
                "Node_en_1",
                "Node_en_2",
                "Node_en_3",
                "Node_en_3",
                "Node_en_3",
                "Node_en_3",
                pd.NA,
            ],
            "de_1": [
                pd.NA,
                "Node_de_1",
                "Node_de_1",
                "Node_de_2",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
                "Node_de_3",
            ],
            "en_2": [
                pd.NA,
                pd.NA,
                "Node_en_1.1",
                pd.NA,
                pd.NA,
                "Node_en_3.1",
                "Node_en_3.2",
                "Node_en_3.2",
                "Node_en_3.2",
            ],
            "de_2": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "Node_de_3.1",
                "Node_de_3.2",
                "Node_de_3.2",
                "Node_de_3.2",
            ],
        }
    )
    return ExcelSheet(excel_name="excel1", sheet_name="sheet1", df=df)


@pytest.fixture()
def f1_s1_no_list_columns() -> ExcelSheet:
    df = pd.DataFrame({"en_list": ["list1", "list1", "list1", "list1"]})
    return ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df)


@pytest.fixture()
def f2_s2_missing_lang_column() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "en_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
            "de_list": ["list1", "list1", "list1", "list1", "list1", "list1", "list1", "list1"],
            "en_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
            "de_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node2", "node3"],
            "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
            "de_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, "node2.1", pd.NA],
            "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )
    return ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df)


@pytest.fixture()
def f2_s2_missing_translations() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "id (optional)": [1, 2, 3, 4, 5, 6, 7],
            "en_list": ["list3", "list3", "list3", "list3", pd.NA, "list3", "list3"],
            "de_list": [pd.NA, "list3", "list3", "list3", "list3", "list3", "list3"],
            "en_1": [pd.NA, pd.NA, "node1", "node1", "node1", pd.NA, "node3"],
            "de_1": [pd.NA, "node1", "node1", "node1", "node1", "node2", "node3"],
            "en_2": [pd.NA, pd.NA, "node1.1", "node1.1", pd.NA, pd.NA, pd.NA],
            "de_2": [pd.NA, pd.NA, "node1.1", "node1.1", "node1.2", pd.NA, pd.NA],
            "en_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA],
            "de_3": [pd.NA, pd.NA, pd.NA, "node1.1.1", pd.NA, pd.NA, pd.NA],
        }
    )
    return ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df)


@pytest.fixture()
def f2_s3_one_row() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "en_list": ["list1"],
            "en_1": ["node1"],
        }
    )
    return ExcelSheet(excel_name="file2", sheet_name="sheet3", df=df)


@pytest.fixture()
def f1_s1_identical_row() -> ExcelSheet:
    df = pd.DataFrame(
        {
            "en_list": ["list1", "list1", "list1", "list1"],
            "en_1": [pd.NA, "node1", "node1", "node3"],
            "id (optional)": [1, 2, 3, 4],
        }
    )
    return ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df)


@pytest.fixture()
def sheets_duplicate_id() -> list[ExcelSheet]:
    df_1 = pd.DataFrame(
        {
            "en_list": ["list1", "list1", "list1", "list1"],
            "en_1": [pd.NA, "node1", "node2", "node3"],
            "id (optional)": [2, 1, 3, 4],
        }
    )
    df_2 = pd.DataFrame(
        {
            "en_list": ["list2", "list2", "list2"],
            "en_1": [pd.NA, "node1", "node3"],
            "id (optional)": [1, 22, 4],
        }
    )
    return [
        ExcelSheet(excel_name="file1", sheet_name="sheet1", df=df_1),
        ExcelSheet(excel_name="file2", sheet_name="sheet2", df=df_2),
    ]
