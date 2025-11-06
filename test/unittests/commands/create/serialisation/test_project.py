from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.serialisation.project import serialise_one_group
from dsp_tools.commands.create.serialisation.project import serialise_one_user_for_creation
from test.unittests.commands.create.constants import PROJECT_IRI


class TestSerialiseGroup:
    def test_one_group(self):
        expected = {
            "name": "NewGroup",
            "descriptions": [
                {"value": "NewGroupDescription", "language": "en"},
                {"value": "NeueGruppenBeschreibung", "language": "de"},
            ],
            "project": PROJECT_IRI,
            "status": True,
            "selfjoin": False,
        }
        group = ParsedGroup(
            "NewGroup",
            descriptions=[
                ParsedGroupDescription("en", "NewGroupDescription"),
                ParsedGroupDescription("de", "NeueGruppenBeschreibung"),
            ],
        )
        result = serialise_one_group(group, PROJECT_IRI)
        assert result == expected


class TestSerialiseUserForCreation:
    def test_only_mandatory(self):
        expected = {
            "username": "user_only_mandatory",
            "email": "user-1@test.org",
            "givenName": "user",
            "familyName": "one",
            "password": "111",
            "lang": "en",
            "status": True,
            "systemAdmin": False,
        }
        user = ParsedUser("user_only_mandatory", "user-1@test.org", "user", "one", "111", "en", False, [])
        result = serialise_one_user_for_creation(user)
        assert result == expected

    def test_is_admin(self):
        pass

    def test_with_group(self):
        pass
