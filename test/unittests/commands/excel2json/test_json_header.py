import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _check_all_users
from dsp_tools.commands.excel2json.json_header import _check_descriptions
from dsp_tools.commands.excel2json.json_header import _check_if_sheets_are_filled_and_exist
from dsp_tools.commands.excel2json.json_header import _check_keywords
from dsp_tools.commands.excel2json.json_header import _check_one_user
from dsp_tools.commands.excel2json.json_header import _check_prefixes
from dsp_tools.commands.excel2json.json_header import _check_project_sheet
from dsp_tools.commands.excel2json.json_header import _do_all_checks
from dsp_tools.commands.excel2json.json_header import _extract_prefixes
from dsp_tools.commands.excel2json.json_header import _extract_project
from dsp_tools.commands.excel2json.json_header import _process_file, _extract_descriptions
from dsp_tools.commands.excel2json.models.input_error import AtLeastOneValueRequiredProblem
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import InvalidExcelContentProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import MoreThanOneRowProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import Users
from test.unittests.commands.excel2json.test_json_header_fixtures import prefixes_good, prefixes_wrong_val, prefixes_missing_val, prefixes_missing_col, project_missing_val, project_missing_col, project_good_missing_zero, project_good_no_zero, project_too_many_rows, user_good, users_good, users_missing_val, users_missing_col, user_wrong_lang, users_wrong_lang, user_wrong_email, user_wrong_role, description_good, description_missing_col, description_missing_val, keywords_good, keywords_missing_col, keywords_missing_val


class TestCheckAll:
    def test_good(
        self,
        prefixes_good: pd.DataFrame,
        project_good_no_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
        users_good: pd.DataFrame,
    ) -> None:
        test_dict = {
            "prefixes": prefixes_good,
            "project": project_good_no_zero,
            "description": description_good,
            "keywords": keywords_good,
            "users": users_good,
        }
        assert not _do_all_checks(test_dict)

    def test_empty_sheet_and_missing_sheet(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
        }
        result = _do_all_checks(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert set(problem.sheet_names) == {"keywords", "prefixes"}

    def test_user_problems(
        self,
        prefixes_good: pd.DataFrame,
        project_good_no_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
        users_wrong_lang: pd.DataFrame,
    ) -> None:
        test_dict = {
            "prefixes": prefixes_good,
            "project": project_good_no_zero,
            "description": description_good,
            "keywords": keywords_good,
            "users": users_wrong_lang,
        }
        result = _do_all_checks(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        sheet_problem = result.problems[0]
        assert isinstance(sheet_problem, ExcelSheetProblem)
        assert sheet_problem.sheet_name == "users"
        assert len(sheet_problem.problems) == 1
        user_problem = sheet_problem.problems[0]
        assert isinstance(user_problem, InvalidExcelContentProblem)
        assert user_problem.expected_content == "One of: en, de, fr, it, rm"
        assert user_problem.actual_content == "other"
        assert user_problem.excel_position.column == "lang"
        assert user_problem.excel_position.row == 2


class TestCheckIfSheetsExist:
    def test_good_with_users(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
            "users": pd.DataFrame({"one": [1]}),
        }
        assert not _check_if_sheets_are_filled_and_exist(test_dict)

    def test_good_no_users(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "description": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
        }
        assert not _check_if_sheets_are_filled_and_exist(test_dict)

    def test_missing_sheet(self) -> None:
        test_dict = {
            "prefixes": pd.DataFrame({"one": [1]}),
            "project": pd.DataFrame({"one": [1]}),
            "keywords": pd.DataFrame({"one": [1]}),
            "users": pd.DataFrame({"one": [1]}),
        }
        result = _check_if_sheets_are_filled_and_exist(test_dict)
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
        result = _check_if_sheets_are_filled_and_exist(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert problem.sheet_names == ["keywords"]


class TestCheckPrefix:
    def test_good(self, prefixes_good: pd.DataFrame) -> None:
        assert not _check_prefixes(prefixes_good)

    def test_missing_value(self, prefixes_missing_val: pd.DataFrame) -> None:
        result = _check_prefixes(prefixes_missing_val)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "prefixes"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        location = problem.locations[0]
        assert location.column == "prefixes"
        assert location.row == 3

    def test_missing_column(self, prefixes_missing_col: pd.DataFrame) -> None:
        result = _check_prefixes(prefixes_missing_col)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "prefixes"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["prefixes"]

    def test_wrong_value(self, prefixes_wrong_val: pd.DataFrame) -> None:
        assert _check_prefixes(prefixes_wrong_val)


class TestCheckProject:
    def test_good(self, project_good_no_zero: pd.DataFrame) -> None:
        assert not _check_project_sheet(project_good_no_zero)

    def test_missing_col(self, project_missing_col: pd.DataFrame) -> None:
        result = _check_project_sheet(project_missing_col)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "project"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["shortcode"]

    def test_more_than_one_row(self, project_too_many_rows: pd.DataFrame) -> None:
        result = _check_project_sheet(project_too_many_rows)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "project"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MoreThanOneRowProblem)
        assert problem.num_rows == 2

    def test_missing_values(self, project_missing_val: pd.DataFrame) -> None:
        result = _check_project_sheet(project_missing_val)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "project"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        location = problem.locations[0]
        assert isinstance(location, PositionInExcel)
        assert location.column == "shortcode"
        assert location.row == 2


class TestCheckDescription:
    def test_good(self, description_good: pd.DataFrame) -> None:
        assert not _check_descriptions(description_good)

    def test_more_than_one_row(self, description_too_many_rows: pd.DataFrame) -> None:
        result = _check_descriptions(description_too_many_rows)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "description"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MoreThanOneRowProblem)
        assert problem.num_rows == 2

    def test_missing_values(self, description_missing_val: pd.DataFrame) -> None:
        result = _check_descriptions(description_missing_val)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "description"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, AtLeastOneValueRequiredProblem)
        expected_cols = {"description_en", "description_de", "description_fr", "description_it", "description_rm"}
        assert set(problem.columns) == expected_cols
        assert problem.row_num == 2

    def test_missing_col(self, description_missing_col: pd.DataFrame) -> None:
        result = _check_descriptions(description_missing_col)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "description"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, AtLeastOneValueRequiredProblem)
        expected_cols = {"description_en", "description_de", "description_fr", "description_it", "description_rm"}
        assert set(problem.columns) == expected_cols
        assert problem.row_num == 2


class TestCheckKeywords:
    def test_good(self, keywords_good: pd.DataFrame) -> None:
        assert not _check_keywords(keywords_good)

    def test_missing_column(self, keywords_missing_col: pd.DataFrame) -> None:
        result = _check_keywords(keywords_missing_col)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "keywords"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["keywords"]

    def test_missing_value(self, keywords_missing_val: pd.DataFrame) -> None:
        result = _check_keywords(keywords_missing_val)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "keywords"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        location = problem.locations[0]
        assert location.column == "keywords"
        assert not location.row


class TestCheckUsers:
    def test_good(self, users_good: pd.DataFrame) -> None:
        assert not _check_all_users(users_good)

    def test_missing_column(self, users_missing_col: pd.DataFrame) -> None:
        result = _check_all_users(users_missing_col)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "users"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, RequiredColumnMissingProblem)
        assert problem.columns == ["password"]

    def test_missing_value(self, users_missing_val: pd.DataFrame) -> None:
        result = _check_all_users(users_missing_val)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "users"
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, MissingValuesProblem)
        assert len(problem.locations) == 1
        location = problem.locations[0]
        assert location.column == "username"
        assert location.row == 2


class TestCheckOneUser:
    def test_good(self, user_good: pd.Series) -> None:
        assert not _check_one_user(user_good, 2)

    def test_bad_lang(self, user_wrong_lang: pd.Series) -> None:
        result = _check_one_user(user_wrong_lang, 2)
        assert len(result) == 1
        problem = result[0]
        assert isinstance(problem, InvalidExcelContentProblem)
        assert problem.expected_content == "One of: en, de, fr, it, rm"
        assert problem.actual_content == "other"
        assert problem.excel_position.column == "lang"
        assert problem.excel_position.row == 2

    def test_bad_email(self, user_wrong_email: pd.Series) -> None:
        result = _check_one_user(user_wrong_email, 2)
        assert len(result) == 1
        problem = result[0]
        assert isinstance(problem, InvalidExcelContentProblem)
        assert problem.expected_content == "A valid email adress"
        assert problem.actual_content == "not an email"
        assert problem.excel_position.column == "email"
        assert problem.excel_position.row == 2

    def test_bad_role(self, user_wrong_role: pd.Series) -> None:
        result = _check_one_user(user_wrong_role, 2)
        assert len(result) == 1
        problem = result[0]
        assert isinstance(problem, InvalidExcelContentProblem)
        assert problem.expected_content == "One of: projectadmin, systemadmin, projectmember"
        assert problem.actual_content == "other"
        assert problem.excel_position.column == "role"
        assert problem.excel_position.row == 2


class TestProcessFile:
    def test_no_user(
        self,
        prefixes_good: pd.DataFrame,
        project_good_no_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
    ) -> None:
        test_dict = {
            "prefixes": prefixes_good,
            "project": project_good_no_zero,
            "description": description_good,
            "keywords": keywords_good,
        }
        result = _process_file(test_dict)
        assert isinstance(result.prefixes, Prefixes)
        assert isinstance(result.project, Project)

    def test_with_user(
        self,
        prefixes_good: pd.DataFrame,
        project_good_missing_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
        users_good: pd.DataFrame,
    ) -> None:
        test_dict = {
            "prefixes": prefixes_good,
            "project": project_good_missing_zero,
            "description": description_good,
            "keywords": keywords_good,
            "users": users_good,
        }
        result = _process_file(test_dict)
        assert isinstance(result.prefixes, Prefixes)
        assert isinstance(result.project, Project)


def test_extract_prefixes(prefixes_good: pd.DataFrame) -> None:
    result = _extract_prefixes(prefixes_good)
    assert isinstance(result, Prefixes)
    assert result.prefixes == {"foaf": "http://xmlns.com/foaf/0.1/", "sdh": "https://ontome.net/ns/sdhss/"}


class TestExtractProject:
    def test_with_users(
        self,
        project_good_missing_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
        users_good: pd.DataFrame,
    ) -> None:
        test_dict = {
            "project": project_good_missing_zero,
            "description": description_good,
            "keywords": keywords_good,
            "users": users_good,
        }
        result = _extract_project(test_dict)
        assert isinstance(result, Project)
        assert result.shortcode == "0011"
        assert result.shortname == "name"
        assert result.longname == "long"
        assert isinstance(result.descriptions, Descriptions)
        assert isinstance(result.keywords, Keywords)
        assert isinstance(result.users, Users)

    def test_no_users(
        self,
        prefixes_good: pd.DataFrame,
        project_good_no_zero: pd.DataFrame,
        description_good: pd.DataFrame,
        keywords_good: pd.DataFrame,
    ) -> None:
        test_dict = {
            "prefixes": prefixes_good,
            "project": project_good_no_zero,
            "description": description_good,
            "keywords": keywords_good,
        }
        result = _extract_project(test_dict)
        assert result.shortcode == "1111"
        assert result.shortname == "name"
        assert result.longname == "long"
        assert isinstance(result.descriptions, Descriptions)
        assert isinstance(result.keywords, Keywords)
        assert not result.users


def test_extract_descriptions(description_good: pd.DataFrame) -> None:
    result = _extract_descriptions(description_good)
    assert isinstance(result, Descriptions)
    assert result.descriptions =={"en": "english", "fr": "french"}


def test_extract_keywords(keywords_good: pd.DataFrame) -> None:
    assert 1 == 0


class TestUsers:
    def test_extract_users(self, users_good: pd.DataFrame) -> None:
        assert 1 == 0

    def test_extract_one_user(self, users_good: pd.DataFrame) -> None:
        assert 1 == 0

    def test_projectadmin(self, users_good: pd.DataFrame) -> None:
        assert 1 == 0

    def test_systemadmin(self, users_good: pd.DataFrame) -> None:
        assert 1 == 0

    def test_other(self, users_good: pd.DataFrame) -> None:
        assert 1 == 0


if __name__ == "__main__":
    pytest.main([__file__])
