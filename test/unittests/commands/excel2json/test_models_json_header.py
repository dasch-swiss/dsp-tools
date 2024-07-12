import pytest

from dsp_tools.commands.excel2json.models.json_header import Description
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import ExcelJsonHeader
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import Users


@pytest.fixture()
def prefixes() -> Prefixes:
    return Prefixes({"dcelements": "http://purl.org/dc/elements/1.1/", "dcterms": "http://purl.org/dc/terms/"})


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
def excel_json_header_no_prefix(project_users: Project) -> ExcelJsonHeader:
    return ExcelJsonHeader(project_users, None)


@pytest.fixture()
def excel_json_header_prefix(project_no_users: Project, prefixes: Prefixes) -> ExcelJsonHeader:
    return ExcelJsonHeader(project_no_users, prefixes)


if __name__ == "__main__":
    pytest.main([__file__])
