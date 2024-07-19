import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _do_formal_compliance
from dsp_tools.commands.excel2json.json_header import _do_prefixes
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.json_header import Prefixes


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
    def test_good(self) -> None:
        pass

    def test_missing_col(self) -> None:
        pass

    def test_missing_value(self) -> None:
        pass


class TestDoDescription:
    def test_good(self) -> None:
        pass

    def test_no_valid_col(self) -> None:
        pass


class TestDoUsers:
    def test_good(self) -> None:
        pass

    def test_missing_col(self) -> None:
        pass

    def test_missing_value(self) -> None:
        pass

    def test_bad_values(self) -> None:
        pass


if __name__ == "__main__":
    pytest.main([__file__])
