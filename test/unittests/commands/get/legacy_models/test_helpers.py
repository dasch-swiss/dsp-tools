from dsp_tools.commands.get.legacy_models.helpers import get_json_ld_id


class TestGetJsonLdId:
    """Tests for the get_json_ld_id helper function."""

    def test_dict_with_id(self) -> None:
        obj = {"@id": "http://example.org/resource/1"}
        assert get_json_ld_id(obj) == "http://example.org/resource/1"

    def test_dict_without_id(self) -> None:
        # Dict exists but has no @id key
        obj = {"@type": "Resource", "label": "Test"}
        assert get_json_ld_id(obj) is None

    def test_empty_dict(self) -> None:
        assert get_json_ld_id({}) is None

    def test_none_input(self) -> None:
        assert get_json_ld_id(None) is None
