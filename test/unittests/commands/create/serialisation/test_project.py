from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.serialisation.project import serialise_one_group
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
    def test_only_mandatory(self):
        pass

    def test_is_admin(self):
        pass

    def test_with_group(self):
        pass
