import pytest

from dsp_tools.commands.excel2json.models.json_header import Description
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import Users


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
    return User(
        "Username1",
        "user1@email.ch",
        "given name1",
        "family name1",
        "PW1",
        "en",
        groups="SystemAdmin",
        projects=":admin",
    )


@pytest.fixture()
def user_member() -> User:
    return User(
        "Username2",
        "user2@email.ch",
        "given name2",
        "family name2",
        "PW2",
        "de",
        groups=None,
        projects=":member",
    )


@pytest.fixture()
def users(user_sys_admin: User, user_member: User) -> Users:
    return Users([user_sys_admin, user_member])


@pytest.fixture()
def project_users(descriptions: Descriptions, keywords: Keywords, users: Users) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, users)


@pytest.fixture()
def project_no_users(descriptions: Descriptions, keywords: Keywords) -> Project:
    return Project("0001", "shortname", "Longname of the project", descriptions, keywords, None)


if __name__ == "__main__":
    pytest.main([__file__])
