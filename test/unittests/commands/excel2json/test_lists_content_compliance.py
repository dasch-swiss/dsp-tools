from typing import cast

import pandas as pd

from dsp_tools.commands.excel2json.lists_content_compliance import _check_one_hierarchy
from dsp_tools.commands.excel2json.lists_content_compliance import _check_one_node_for_translations
from dsp_tools.commands.excel2json.lists_content_compliance import _test_all_nodes_translated_into_all_languages
from dsp_tools.commands.excel2json.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.models.input_error import MissingTranslationsSheetProblem


class TestAllNodesTranslatedIntoAllLanguages:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
                "index": [0, 1, 2, 3, 4, 5, 6, 7, 8],
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
        assert not _test_all_nodes_translated_into_all_languages(test_df, "sheet")

    def test_missing_translation(self) -> None:
        test_df = pd.DataFrame(
            {
                "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
                "row_number": [2, 3, 4, 5, 6, 7, 8, 9, 10],
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
        expected = [
            MissingNodeTranslationProblem(["en_list"], 7),
            MissingNodeTranslationProblem(["en_1"], 10),
            MissingNodeTranslationProblem(["en_2"], 4),
        ]
        result = _test_all_nodes_translated_into_all_languages(test_df, "sheet")
        result = cast(MissingTranslationsSheetProblem, result)
        for res, expct in zip(result.node_problems, expected):
            assert res.empty_columns == expct.empty_columns
            assert res.row_num == expct.row_num


class TestCheckOneHierarchy:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "en_1": ["exist1_en", "exist2_en", "exist3_en"],
                "de_1": ["exist1_de", "exist2_de", "exist3_de"],
                "fr_1": ["exist1_fr", "exist2_fr", "exist3_fr"],
                "index": [1, 2, 3],
            }
        )
        assert not _check_one_hierarchy(["en_1", "de_1", "fr_1", "index"], test_df)

    def test_missing_translation(self) -> None:
        test_df = pd.DataFrame(
            {
                "en_1": ["exist1_en", pd.NA, "exist3_en"],
                "de_1": ["exist1_de", pd.NA, "exist3_de"],
                "fr_1": ["exist1_fr", "exist2_fr", "exist3_fr"],
                "index": [1, 2, 3],
            }
        )
        res = _check_one_hierarchy(["en_1", "de_1", "fr_1", "index"], test_df)
        assert len(res) == 1
        prbl = res[0]
        assert prbl.empty_columns == ["en_1", "de_1"]
        assert prbl.row_num == 2


class TestCheckOneNodeForTranslation:
    def test_good(self) -> None:
        test_series = pd.Series(["exist_en", "exist_de"], index=["en_1", "de_1"])
        assert not _check_one_node_for_translations(test_series)

    def test_missing_translation(self) -> None:
        test_series = pd.Series(["exist_en", pd.NA, 3], index=["en_1", "de_1", "index"])
        result = _check_one_node_for_translations(test_series)
        result = cast(MissingNodeTranslationProblem, result)
        assert result.empty_columns == ["de_1"]
        assert result.row_num == 3
