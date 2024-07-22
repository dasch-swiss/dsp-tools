import pandas as pd
import pytest

from dsp_tools.commands.excel2json.json_header import _check_email
from dsp_tools.commands.excel2json.json_header import _check_lang
from dsp_tools.commands.excel2json.json_header import _check_project_sheet
from dsp_tools.commands.excel2json.json_header import _do_description
from dsp_tools.commands.excel2json.json_header import _do_formal_compliance
from dsp_tools.commands.excel2json.json_header import _do_keywords
from dsp_tools.commands.excel2json.json_header import _do_one_user
from dsp_tools.commands.excel2json.json_header import _do_prefixes
from dsp_tools.commands.excel2json.json_header import _do_users
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
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import UserRole
from dsp_tools.commands.excel2json.models.json_header import Users


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
    def test_good(self) -> None:
        project_sheet = pd.DataFrame({"shortcode": ["0001"], "shortname": ["name"], "longname": ["long"]})
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
        position = problem.locations[0]
        assert isinstance(position, PositionInExcel)
        assert position.column == "keywords"


class TestDoUsers:
    def test_good(self) -> None:
        test_df = pd.DataFrame(
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
        result = _do_users(test_df)
        assert isinstance(result, Users)
        assert len(result.users) == 2
        resulting_users = sorted(result.users, key=lambda x: x.username)
        alice = resulting_users[0]
        assert alice.username == "Alice"
        assert alice.email == "alice@dasch.swiss"
        assert alice.givenName == "Alice Pleasance"
        assert alice.familyName == "Liddell"
        assert alice.password == "alice4322"
        assert alice.lang == "fr"
        alice_role = alice.role
        assert isinstance(alice_role, UserRole)
        assert not alice_role.project_admin
        assert alice_role.sys_admin

        caterpillar = resulting_users[1]
        assert caterpillar.username == "Caterpillar"
        assert caterpillar.email == "caterpillar@dasch.swiss"
        assert caterpillar.givenName == "Caterpillar"
        assert caterpillar.familyName == "Wonderland"
        assert caterpillar.password == "alice7652"
        assert caterpillar.lang == "de"
        caterpillar_role = caterpillar.role
        assert isinstance(caterpillar_role, UserRole)
        assert not caterpillar_role.project_admin
        assert not caterpillar_role.sys_admin

    def test_missing_col(self) -> None:
        test_df = pd.DataFrame(
            {
                "email": ["alice@dasch.swiss", "caterpillar@dasch.swiss"],
                "givenname": ["Alice Pleasance", "Caterpillar"],
                "familyname": ["Liddell", "Wonderland"],
                "password": ["alice4322", "alice7652"],
                "lang": ["fr", "de"],
                "role": ["systemadmin", "projectmember"],
            }
        )
        result = _do_users(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "users"
        assert len(result.problems) == 1
        missing = result.problems[0]
        assert isinstance(missing, RequiredColumnMissingProblem)
        assert missing.columns == ["username"]

    def test_missing_value(self) -> None:
        test_df = pd.DataFrame(
            {
                "username": ["Alice", "Caterpillar"],
                "email": ["alice@dasch.swiss", "caterpillar@dasch.swiss"],
                "givenname": ["Alice Pleasance", "Caterpillar"],
                "familyname": ["Liddell", "Wonderland"],
                "password": ["alice4322", pd.NA],
                "lang": ["fr", "de"],
                "role": ["systemadmin", "projectmember"],
            }
        )
        result = _do_users(test_df)
        assert isinstance(result, ExcelSheetProblem)
        assert result.sheet_name == "users"
        assert len(result.problems) == 1
        empty = result.problems[0]
        assert isinstance(empty, MissingValuesProblem)
        assert len(empty.locations) == 1
        location = empty.locations[0]
        assert isinstance(location, PositionInExcel)
        assert location.column == "password"
        assert location.row == 3


class TestDoOneUser:
    def test_good(self) -> None:
        test_series = pd.Series(
            {
                "username": "Alice",
                "email": "alice@dasch.swiss",
                "givenname": "Alice Pleasance",
                "familyname": "Liddell",
                "password": "alice4322",
                "lang": "en",
                "role": "projectadmin",
            }
        )
        result = _do_one_user(test_series, 1)
        assert isinstance(result, User)
        assert result.username == "Alice"
        assert result.email == "alice@dasch.swiss"
        assert result.givenName == "Alice Pleasance"
        assert result.familyName == "Liddell"
        assert result.password == "alice4322"
        assert result.lang == "en"
        role = result.role
        assert isinstance(role, UserRole)
        assert role.project_admin
        assert not role.sys_admin

    def test_bad_lang(self) -> None:
        test_series = pd.Series(
            {
                "username": "Alice",
                "email": "alice@dasch.swiss",
                "givenName": "Alice Pleasance",
                "familyName": "Liddell",
                "password": "alice4322",
                "lang": "other",
                "role": "projectadmin",
            },
        )
        result = _do_one_user(test_series, 2)
        assert isinstance(result, list)
        assert len(result) == 1
        problem = result[0]
        assert isinstance(problem, InvalidExcelContentProblem)
        assert problem.expected_content == "One of: en, de, fr, it, rm"
        assert problem.actual_content == "other"
        position = problem.excel_position
        assert isinstance(position, PositionInExcel)
        assert position.column == "lang"
        assert position.row == 2


class TestGetRole:
    def test_get_role_projectadmin(self) -> None:
        result = _get_role("projectadmin", 1)
        assert isinstance(result, UserRole)
        assert not result.sys_admin
        assert result.project_admin

    def test_get_role_systemadmin(self) -> None:
        result = _get_role("systemadmin", 1)
        assert isinstance(result, UserRole)
        assert result.sys_admin
        assert not result.project_admin

    def test_get_role_projectmember(self) -> None:
        result = _get_role("projectmember", 1)
        assert isinstance(result, UserRole)
        assert not result.sys_admin
        assert not result.project_admin

    def test_get_role_bad(self) -> None:
        result = _get_role("wrong", 1)
        assert isinstance(result, InvalidExcelContentProblem)
        assert result.expected_content == "One of: projectadmin, systemadmin, projectmember"
        assert result.actual_content == "wrong"
        position = result.excel_position
        assert isinstance(position, PositionInExcel)
        assert position.column == "role"
        assert position.row == 1


def test_get_lang_good() -> None:
    assert not _check_lang("en", 1)


def test_get_lang_bad() -> None:
    result = _check_lang("other", 1)
    assert isinstance(result, InvalidExcelContentProblem)
    assert result.expected_content == "One of: en, de, fr, it, rm"
    assert result.actual_content == "other"
    position = result.excel_position
    assert isinstance(position, PositionInExcel)
    assert position.column == "lang"
    assert position.row == 1


def test_check_email_bad() -> None:
    result = _check_email("bad", 1)
    assert isinstance(result, InvalidExcelContentProblem)
    assert result.expected_content == "A valid email adress"
    assert result.actual_content == "bad"
    position = result.excel_position
    assert isinstance(position, PositionInExcel)
    assert position.column == "email"
    assert position.row == 1


def test_check_email_good() -> None:
    assert not _check_email("alice@dasch.swiss", 1)


if __name__ == "__main__":
    pytest.main([__file__])
