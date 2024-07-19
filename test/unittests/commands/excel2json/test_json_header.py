import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _do_formal_compliance
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem


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


if __name__ == "__main__":
    pytest.main([__file__])
