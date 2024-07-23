import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _check_email, _do_all_checks
from dsp_tools.commands.excel2json.json_header import _check_if_sheets_are_filled_and_exist
from dsp_tools.commands.excel2json.json_header import _check_lang
from dsp_tools.commands.excel2json.json_header import _check_project_sheet
from dsp_tools.commands.excel2json.json_header import _extract_descriptions
from dsp_tools.commands.excel2json.json_header import _extract_keywords
from dsp_tools.commands.excel2json.json_header import _extract_one_user
from dsp_tools.commands.excel2json.json_header import _extract_prefixes
from dsp_tools.commands.excel2json.json_header import _extract_project
from dsp_tools.commands.excel2json.json_header import _extract_users
from dsp_tools.commands.excel2json.json_header import _get_description_cols
from dsp_tools.commands.excel2json.json_header import _get_role
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
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import UserRole
from dsp_tools.commands.excel2json.models.json_header import Users


@pytest.fixture()
def prefixes_good() -> pd.DataFrame:
    return pd.DataFrame(
        {"prefixes": ["foaf:", "sdh"], "uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]}
    )


@pytest.fixture()
def prefixes_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]})


@pytest.fixture()
def prefixes_missing_val() -> pd.DataFrame:
    return pd.DataFrame(
        {"prefixes": ["foaf:", pd.NA], "uri": ["http://xmlns.com/foaf/0.1/", "https://ontome.net/ns/sdhss/"]}
    )


@pytest.fixture()
def prefixes_wrong_val() -> pd.DataFrame:
    return pd.DataFrame({"prefixes": ["foaf:", "sdh"], "uri": ["http://xmlns.com/foaf/0.1/", "not a uri"]})


@pytest.fixture()
def project_good_missing_zero() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [11], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture()
def project_good_no_zero() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [1111], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture()
def project_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"shortname": ["name"], "longname": ["long"]})


@pytest.fixture()
def project_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [pd.NA], "shortname": ["name"], "longname": ["long"]})


@pytest.fixture()
def project_too_many_rows() -> pd.DataFrame:
    return pd.DataFrame({"shortcode": [11, 0], "shortname": ["name", pd.NA], "longname": ["long", "other"]})


@pytest.fixture()
def description_good() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description_en": ["english"],
            "description_de": [pd.NA],
            "fr": ["french"],
            "description_rm": [pd.NA],
        }
    )


@pytest.fixture()
def description_too_many_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "description_en": ["english", "en1"],
            "description_de": [pd.NA, pd.NA],
            "fr": ["french", "french2"],
            "description_it": [pd.NA, "it"],
            "description_rm": [pd.NA, pd.NA],
        }
    )


@pytest.fixture()
def description_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"other": ["english"]})


@pytest.fixture()
def description_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"other": ["english"], "description_en": [pd.NA]})


@pytest.fixture()
def keywords_good() -> pd.DataFrame:
    pd.DataFrame({"keywords": ["one", pd.NA, "three"]})


@pytest.fixture()
def keywords_missing_col() -> pd.DataFrame:
    return pd.DataFrame({"other": [1]})


@pytest.fixture()
def keywords_missing_val() -> pd.DataFrame:
    return pd.DataFrame({"other": [1], "keywords": [pd.NA]})


@pytest.fixture()
def users_good() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice", "Caterpillar"],
            "email": ["alice@dasch.swiss", "caterpillar@dasch.swiss"],
            "givenname": ["Alice Pleasance", "Caterpillar"],
            "familyname": ["Liddell", "Wonderland"],
            "password": ["alice4322", "alice7652"],
            "lang": ["fr", "de"],
            "role": ["systemadmin", "projectmember"],
        }
    )


@pytest.fixture()
def users_missing_col() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "lang": ["fr"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture()
def users_missing_val() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": [pd.NA],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["fr"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture()
def users_wrong_lang() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["other"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture()
def users_wrong_email() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["not an email"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["fr"],
            "role": ["systemadmin"],
        }
    )


@pytest.fixture()
def users_wrong_role() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "username": ["Alice"],
            "email": ["alice@dasch.swiss"],
            "givenname": ["Alice Pleasance"],
            "familyname": ["Liddell"],
            "password": ["alice7652"],
            "lang": ["fr"],
            "role": ["other"],
        }
    )


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
        result = _check_if_sheets_are_filled_and_exist(test_dict)
        assert isinstance(result, ExcelFileProblem)
        assert len(result.problems) == 1
        problem = result.problems[0]
        assert isinstance(problem, EmptySheetsProblem)
        assert set(problem.sheet_names) == {"keywords", "prefixes"}

    def test_user_problems(self) -> None:
        assert 1 == 0


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
    def test_good(self) -> None:
        assert 1 == 0

    def test_missing_value(self) -> None:
        assert 1 == 0

    def test_missing_column(self) -> None:
        assert 1 == 0


class TestCheckProject:
    def test_good(self) -> None:
        assert 1 == 0

    def test_missing_col(self) -> None:
        assert 1 == 0

    def test_more_than_one_row(self) -> None:
        assert 1 == 0

    def test_missing_values(self) -> None:
        assert 1 == 0


class TestCheckDescription:
    def test_good(self) -> None:
        assert 1 == 0

    def test_more_than_one_row(self) -> None:
        assert 1 == 0

    def test_missing_values(self) -> None:
        assert 1 == 0


class TestCheckKeywords:
    def test_good(self) -> None:
        assert 1 == 0

    def test_missing_column(self) -> None:
        assert 1 == 0

    def test_missing_value(self) -> None:
        assert 1 == 0


class TestCheckUsers:
    def test_good(self) -> None:
        assert 1 == 0

    def test_missing_column(self) -> None:
        assert 1 == 0

    def test_missing_value(self) -> None:
        assert 1 == 0


class TestCheckOneUser:
    def test_good(self) -> None:
        assert 1 == 0

    def test_bad_lang(self) -> None:
        assert 1 == 0

    def test_bad_email(self) -> None:
        assert 1 == 0

    def test_bad_role(self) -> None:
        assert 1 == 0


class TestProcessFile:
    def test_no_user(self) -> None:
        assert 1 == 0

    def test_with_user(self) -> None:
        assert 1 == 0


class TestExtractPrefixes:
    def test_with_colon(self) -> None:
        assert 1 == 0

    def test_no_colon(self) -> None:
        assert 1 == 0


class TestExtractProject:
    def test_with_users(self) -> None:
        assert 1 == 0

    def test_no_users(self) -> None:
        assert 1 == 0

    def test_shortcode_with_leading_zero(self) -> None:
        assert 1 == 0

    def test_shortcode_without_leading_zero(self) -> None:
        assert 1 == 0


class TestExtractDescriptions:
    def test_mixed_col_names(self) -> None:
        assert 1 == 0

    def test_standard_cols(self) -> None:
        assert 1 == 0


def test_extract_keywords() -> None:
    assert 1 == 0


class TestUsers:
    def test_extract_users(self) -> None:
        assert 1 == 0

    def test_extract_one_user(self) -> None:
        assert 1 == 0

    def test_projectadmin(self) -> None:
        assert 1 == 0

    def test_systemadmin(self) -> None:
        assert 1 == 0

    def test_other(self) -> None:
        assert 1 == 0


if __name__ == "__main__":
    pytest.main([__file__])
