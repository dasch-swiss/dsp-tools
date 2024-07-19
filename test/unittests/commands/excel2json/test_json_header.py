import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _check_project_sheet
from dsp_tools.commands.excel2json.json_header import _do_description
from dsp_tools.commands.excel2json.json_header import _do_formal_compliance
from dsp_tools.commands.excel2json.json_header import _do_keywords
from dsp_tools.commands.excel2json.json_header import _do_prefixes
from dsp_tools.commands.excel2json.json_header import _get_description_cols
from dsp_tools.commands.excel2json.json_header import _is_email
from dsp_tools.commands.excel2json.models.input_error import AtLeastOneValueRequiredProblem
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import MoreThanOneRowProblem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Prefixes


@pytest.fixture()
def project_sheet() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": ["0001"], "shortname": ["name"], "longname": ["long"]})


class TestFormalCompliance:
    def test_good(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
            "users": pd.DataFrame({}),
        }
        assert not _do_formal_compliance(test_dict)

    def test_good_no_users(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
        }
        assert not _do_formal_compliance(test_dict)

    def test_missing_sheet(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
            "users": pd.DataFrame({"one": [1]}),
        }
        result = _do_formal_compliance(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert problem.sheet_names == ["description"]

    def test_empty_sheet(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({}),
        }
        result = _do_formal_compliance(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert problem.sheet_names == ["keywords"]

    def test_empty_sheet_and_missing_sheet(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
        }
        result = _do_formal_compliance(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert set(problem.sheet_names) == {"keywords", "prefixes"}


class TestProcessFile:
    def test_good(self) -> None:
        pass

    def test_bad(self) -> None:
        pass


class TestDoPrefix:
    def test_good(self) -> None:
        test_df = pd.DataFrame({"prefixes": ["pref:"], "uri": ["namespace"]})
        result = _do_prefixes(test_df)
        assert isinstance(result, Prefixes)
        assert result.prefixes == {"pref": "namespace"}

    def test_missing_col(self) -> None:
        test_df = pd.DataFrame({"uri": ["namespace"]})
        result = _do_prefixes(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["prefixes"]

    def test_missing_value(self) -> None:
        test_df = pd.DataFrame({"prefixes": ["pref:", pd.NA], "uri": ["namespace", "other_namespace"]})
        result = _do_prefixes(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "prefixes"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        loc = problem.locations[0]
        assert loc.column == "prefixes"
        assert loc.row == 3


class TestDoProject:
    def test_good_with_users(self) -> None:
        pass

    def test_good_no_users(self) -> None:
        pass

    def test_project_bad_project(self) -> None:
        pass

    def test_project_bad_keywords(self) -> None:
        pass

    def test_project_bad_descriptions(self) -> None:
        pass

    def test_project_bad_users(self) -> None:
        pass


class TestDoProjectChecks:
    def test_good(self, project_sheet: pd.DataFrame) -> None:
        result = _check_project_sheet(project_sheet)
        assert not result

    def test_missing_col(self) -> None:
        test_df = pd.DataFrame({"shortcode": [], "longname": []})
        result = _check_project_sheet(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["shortname"]

    def test_missing_value(self) -> None:
        test_df = pd.DataFrame({"shortcode": ["0001"], "shortname": [pd.NA], "longname": ["long"]})
        result = _check_project_sheet(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        loc = problem.locations[0]
        assert loc.row == 2
        assert loc.column == "shortname"

    def test_too_many_rows(self) -> None:
        test_df = pd.DataFrame({"shortcode": ["0001", "2"], "shortname": ["name", "2"], "longname": ["long", "2"]})
        result = _check_project_sheet(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MoreThanOneRowProblem)
        assert problem.num_rows == 2


class TestDoDescription:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "description_en": ["english"],
                "description_de": [pd.NA],
                "description_fr": ["french"],
                "description_it": [pd.NA],
                "description_rm": [pd.NA],
            }
        )
        res = _do_description(test_df)
        assert isinstance(res, Descriptions)
        assert res.descriptions == {"en": "english", "fr": "french"}

    def test_good_mixed_cols(self) -> None:
        test_df = pd.DataFrame(
            {
                "description_en": [pd.NA],
                "description_de": ["german"],
                "fr": ["french"],
                "description_it": [pd.NA],
            }
        )
        res = _do_description(test_df)
        assert isinstance(res, Descriptions)
        assert res.descriptions == {"de": "german", "fr": "french"}

    def test_too_long(self) -> None:
        test_df = pd.DataFrame({"one": [1, 2]})
        res = _do_description(test_df)
        assert isinstance(res, ExcelSheetProblem)
        assert len(res.problems) == 1
        problem = res.problems[0]
        assert isinstance(problem, MoreThanOneRowProblem)
        assert problem.num_rows == 2

    def test_no_values_filled(self) -> None:
        test_df = pd.DataFrame({"description_en": [pd.NA], "random": ["value"]})
        res = _do_description(test_df)
        assert isinstance(res, ExcelSheetProblem)
        assert len(res.problems) == 1
        problem = res.problems[0]
        assert isinstance(problem, AtLeastOneValueRequiredProblem)
        assert problem.row_num == 1
        description_cols = {"description_en", "description_de", "description_fr", "description_it", "description_rm"}
        assert set(problem.columns) == description_cols

    def test_no_valid_col(self) -> None:
        test_df = pd.DataFrame({"description_es": [1]})
        res = _do_description(test_df)
        assert isinstance(res, ExcelSheetProblem)
        assert len(res.problems) == 1
        problem = res.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        description_cols = {"description_en", "description_de", "description_fr", "description_it", "description_rm"}
        assert set(problem.columns) == description_cols

    def test_get_description_cols_found(self) -> None:
        test_cols = ["description_en", "description_xy", "fr"]
        assert _get_description_cols(test_cols) == {"en": "description_en", "fr": "fr"}

    def test_get_description_cols_none(self) -> None:
        test_cols = ["description_xy", "isadfahfas"]
        assert not _get_description_cols(test_cols)


class TestDoKeywords:
    def test_good(self) -> None:
        test_df = pd.DataFrame({"keywords": ["one", pd.NA, "three"]})
        result = _do_keywords(test_df)
        assert isinstance(result, Keywords)
        assert result.serialise() == ["one", "three"]

    def test_missing_col(self) -> None:
        test_df = pd.DataFrame({"other": ["other"]})
        result = _do_keywords(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["keywords"]

    def test_missing_value(self) -> None:
        test_df = pd.DataFrame({"keywords": [pd.NA], "other": ["other"]})
        result = _do_keywords(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1


class TestDoUsers:
    def test_good(self) -> None:
        pass

    def test_missing_col(self) -> None:
        pass

    def test_missing_value(self) -> None:
        pass

    def test_bad_values(self) -> None:
        pass

    def test_is_email_good(self) -> None:
        assert not _is_email("sadfkjdfsa")

    def test_is_email_bad(self) -> None:
        assert _is_email("alice@dasch.swiss")


if __name__ == "__main__":
    pytest.main([__file__])
