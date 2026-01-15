

from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.serialisation.project import serialise_one_group
from dsp_tools.commands.create.serialisation.project import serialise_one_user_for_creation
from dsp_tools.commands.create.serialisation.project import serialise_project
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


class TestSerialiseUser:
    def test_user(self):
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
        user = ParsedUser("user_only_mandatory", "user-1@test.org", "user", "one", "111", "en")
        result = serialise_one_user_for_creation(user)
        assert result == expected


class TestSerialiseProject:
    def test_with_license(self):
        proj = ParsedProjectMetadata(
            shortcode="0001",
            shortname="name",
            longname="long",
            descriptions={"en": "english", "de": "german"},
            keywords=["test"],
            enabled_licenses=["license"],
        )
        expected = {
            "shortcode": "0001",
            "shortname": "name",
            "longname": "long",
            "description": [{"language": "en", "value": "english"}, {"language": "de", "value": "german"}],
            "keywords": ["test"],
            "status": True,
            "selfjoin": False,
            "enabledLicenses": ["license"],
        }
        result = serialise_project(proj)
        assert result == expected

    def test_no_license(self):
        proj = ParsedProjectMetadata(
            shortcode="0001",
            shortname="name",
            longname="long",
            descriptions={"en": "english"},
            keywords=["test"],
            enabled_licenses=[],
        )
        expected = {
            "shortcode": "0001",
            "shortname": "name",
            "longname": "long",
            "description": [{"language": "en", "value": "english"}],
            "keywords": ["test"],
            "status": True,
            "selfjoin": False,
        }
        result = serialise_project(proj)
        assert result == expected
