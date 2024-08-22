from typing import Any

import pytest

from dsp_tools.commands.xml_validate.deserialise_project import _deserialise_one_list


def test_deserialise_lists(list_from_api: dict[str, Any]) -> None:
    res = _deserialise_one_list(list_from_api)
    assert res.list_name == "onlyList"
    assert set(res.nodes) == {"n1", "n1.1", "n1.1.1"}


class TestDeserialiseResource:
    def test_get_resource_classes(self, onto_json: dict[str, Any]) -> None:
        pass

    def test_deserialise_one_resource_class(self, one_res_class: dict[str, Any]) -> None:
        pass

    def test_get_restrictions(self, one_res_class: dict[str, Any]) -> None:
        pass


class TestDeserialiseProperties:
    def test_get_all_onto_properties(self, onto_json: dict[str, Any]) -> None:
        pass

    def test_list_value(self, list_prop: dict[str, Any]) -> None:
        pass

    def test_link_prop(self: dict[str, Any]) -> None:
        pass

    def test_simpletext_prop(self: dict[str, Any]) -> None:
        pass


if __name__ == "__main__":
    pytest.main([__file__])
