import pytest

from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Licenses
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import UserRole
from dsp_tools.commands.excel2json.models.json_header import Users

SCHEMA = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"


@pytest.fixture
def prefixes() -> Prefixes:
    return Prefixes({"dcelements": "http://purl.org/dc/elements/1.1/"})


@pytest.fixture
def descriptions() -> Descriptions:
    return Descriptions({"de": "Beschreibungstext", "en": "description text"})


@pytest.fixture
def keywords() -> Keywords:
    return Keywords(["Keyword 1"])


@pytest.fixture
def licenses() -> Licenses:
    return Licenses(["http://rdfh.ch/licenses/cc-by-4.0"])


@pytest.fixture
def user_sys_admin() -> User:
    return User("sys_admin", "sys_admin@email.ch", "given name1", "family name1", "PW1", "en", UserRole(sys_admin=True))


@pytest.fixture
def user_member() -> User:
    return User("member", "member@email.ch", "given name2", "family name2", "PW2", "de", UserRole())


@pytest.fixture
def user_admin() -> User:
    return User("admin", "admin@email.ch", "given name3", "family name3", "PW3", "de", UserRole(project_admin=True))


@pytest.fixture
def users(user_sys_admin: User, user_member: User, user_admin: User) -> Users:
    return Users([user_sys_admin, user_member, user_admin])


@pytest.fixture
def project_with_users(descriptions: Descriptions, keywords: Keywords, licenses: Licenses, users: Users) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, licenses, users)


@pytest.fixture
def project_no_users(descriptions: Descriptions, keywords: Keywords, licenses: Licenses) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, licenses, None)


@pytest.fixture
def project_no_licenses(descriptions: Descriptions, keywords: Keywords) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, Licenses([]), None)


@pytest.fixture
def filled_json_header_with_users_without_prefix(project_with_users: Project) -> FilledJsonHeader:
    return FilledJsonHeader(project_with_users, None)


@pytest.fixture
def filled_json_header_with_users_with_prefix(project_no_users: Project, prefixes: Prefixes) -> FilledJsonHeader:
    return FilledJsonHeader(project_no_users, prefixes)


def test_filled_json_header_with_users_without_prefix(
    filled_json_header_with_users_without_prefix: FilledJsonHeader,
) -> None:
    expected = {
        "$schema": SCHEMA,
        "project": {
            "shortcode": "0001",
            "shortname": "shortname",
            "longname": "Longname of the project",
            "descriptions": {"de": "Beschreibungstext", "en": "description text"},
            "keywords": ["Keyword 1"],
            "enabled_licenses": ["http://rdfh.ch/licenses/cc-by-4.0"],
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
    res = filled_json_header_with_users_without_prefix.to_dict()
    assert res == expected


def test_filled_json_header_with_users_with_prefix(filled_json_header_with_users_with_prefix: FilledJsonHeader) -> None:
    expected = {
        "prefixes": {"dcelements": "http://purl.org/dc/elements/1.1/"},
        "$schema": SCHEMA,
        "project": {
            "shortcode": "0001",
            "shortname": "shortname",
            "longname": "Longname of the project",
            "descriptions": {"de": "Beschreibungstext", "en": "description text"},
            "keywords": ["Keyword 1"],
            "enabled_licenses": ["http://rdfh.ch/licenses/cc-by-4.0"],
        },
    }
    res = filled_json_header_with_users_with_prefix.to_dict()
    assert res == expected


def test_filled_json_header_no_license(project_no_licenses: Project) -> None:
    header = FilledJsonHeader(project_no_licenses, None)
    expected = {
        "$schema": SCHEMA,
        "project": {
            "shortcode": "0001",
            "shortname": "shortname",
            "longname": "Longname of the project",
            "descriptions": {"de": "Beschreibungstext", "en": "description text"},
            "keywords": ["Keyword 1"],
            "enabled_licenses": [],
        },
    }
    res = header.to_dict()
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
