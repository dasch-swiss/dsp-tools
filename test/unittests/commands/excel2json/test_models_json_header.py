import pytest

from dsp_tools.commands.excel2json.models.json_header import Description
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import ExcelJsonHeader
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import Users

SCHEMA = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"


@pytest.fixture()
def prefixes() -> Prefixes:
    return Prefixes({"dcelements": "http://purl.org/dc/elements/1.1/"})


@pytest.fixture()
def description_de() -> Description:
    return Description("de", "Beschreibungstext")


@pytest.fixture()
def description_en() -> Description:
    return Description("en", "description text")


@pytest.fixture()
def descriptions(description_de: Description, description_en: Description) -> Descriptions:
    return Descriptions([description_de, description_en])


@pytest.fixture()
def keywords() -> Keywords:
    return Keywords(["Keyword 1"])


@pytest.fixture()
def user_sys_admin() -> User:
    return User("sys_admin", "sys_admin@email.ch", "given name1", "family name1", "PW1", "en", sys_admin=True)


@pytest.fixture()
def user_member() -> User:
    return User("member", "member@email.ch", "given name2", "family name2", "PW2", "de", member=True)


@pytest.fixture()
def user_admin() -> User:
    return User("admin", "admin@email.ch", "given name3", "family name3", "PW3", "de", admin=True)


@pytest.fixture()
def users(user_sys_admin: User, user_member: User, user_admin: User) -> Users:
    return Users([user_sys_admin, user_member, user_admin])


@pytest.fixture()
def project_users(descriptions: Descriptions, keywords: Keywords, users: Users) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, users)


@pytest.fixture()
def project_no_users(descriptions: Descriptions, keywords: Keywords) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, None)


@pytest.fixture()
def excel_json_header_no_prefix_users(project_users: Project) -> ExcelJsonHeader:
    return ExcelJsonHeader(project_users, None)


@pytest.fixture()
def excel_json_header_prefix_no_users(project_no_users: Project, prefixes: Prefixes) -> ExcelJsonHeader:
    return ExcelJsonHeader(project_no_users, prefixes)


def test_excel_json_header_no_prefix_users(excel_json_header_no_prefix_users: ExcelJsonHeader) -> None:
    expected = {
        "$schema": SCHEMA,
        "project": {
            "shortcode": "0001",
            "shortname": "shortname",
            "longname": "Longname of the project",
            "descriptions": {"de": "Beschreibungstext", "en": "description text"},
            "keywords": ["Keyword 1"],
            "users": [
                {
                    "username": "sys_admin",
                    "email": "sys_admin@email.ch",
                    "givenName": "given name1",
                    "familyName": "family name1",
                    "password": "PW1",
                    "lang": "en",
                    "status": True,
                    "groups": ["SystemAdmin"],
                    "projects": [":admin", ":member"],
                },
                {
                    "username": "member",
                    "email": "member@email.ch",
                    "givenName": "given name2",
                    "familyName": "family name2",
                    "password": "PW2",
                    "lang": "de",
                    "status": True,
                    "projects": [":member"],
                },
                {
                    "username": "admin",
                    "email": "admin@email.ch",
                    "givenName": "given name3",
                    "familyName": "family name3",
                    "password": "PW3",
                    "lang": "de",
                    "status": True,
                    "projects": [":admin", ":member"],
                },
            ],
        },
    }
    res = excel_json_header_no_prefix_users.make()
    assert res == expected


def test_excel_json_header_prefix_no_users(excel_json_header_prefix_no_users: ExcelJsonHeader) -> None:
    expected = {
        "prefixes": {"dcelements": "http://purl.org/dc/elements/1.1/"},
        "$schema": SCHEMA,
        "project": {
            "shortcode": "0001",
            "shortname": "shortname",
            "longname": "Longname of the project",
            "descriptions": {"de": "Beschreibungstext", "en": "description text"},
            "keywords": ["Keyword 1"],
        },
    }
    res = excel_json_header_prefix_no_users.make()
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
