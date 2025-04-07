import pytest
from pytest_unordered import unordered

from dsp_tools.commands.project.create.parse_project import _rectify_hlist_of_properties
from dsp_tools.error.exceptions import InputError


def test_rectify_hlist_of_properties() -> None:
    lists = [
        {
            "name": "list-no-1",
            "labels": {"en": "List number one", "de": "Liste Nummer eins"},
            "nodes": [{"name": "first node", "labels": {"en": "First node"}}],
        },
        {
            "name": "list-no-2",
            "labels": {"en": "List number two", "de": "Liste Nummer zwei"},
            "nodes": [{"name": "second node", "labels": {"en": "second node"}}],
        },
    ]
    properties = [
        {
            "name": "hasList1",
            "super": ["hasValue"],
            "object": "ListValue",
            "labels": {"en": "hasList1"},
            "gui_element": "List",
            "gui_attributes": {"hlist": "List number one"},
        },
        {
            "name": "hasList2",
            "super": ["hasValue"],
            "object": "ListValue",
            "labels": {"en": "hasList2"},
            "gui_element": "List",
            "gui_attributes": {"hlist": "Liste Nummer zwei"},
        },
    ]
    properties_returned = _rectify_hlist_of_properties(
        lists=lists,
        properties=properties,
    )
    returned_hlists = [x["gui_attributes"]["hlist"] for x in properties_returned]
    expected_hlists = ["list-no-1", "list-no-2"]
    assert unordered(returned_hlists) == expected_hlists


def test_rectify_hlist_of_properties_nonexisting_list() -> None:
    lists = [
        {
            "name": "list-no-1",
            "labels": {"en": "List number one", "de": "Liste Nummer eins"},
            "nodes": [{"name": "first node", "labels": {"en": "First node"}}],
        }
    ]
    properties = [
        {
            "name": "hasList1",
            "super": ["hasValue"],
            "object": "ListValue",
            "labels": {"en": "hasList1"},
            "gui_element": "List",
            "gui_attributes": {"hlist": "Nonexisting list"},
        }
    ]
    with pytest.raises(
        InputError,
        match=r"Property 'hasList1' references an unknown list: 'Nonexisting list'",
    ):
        _rectify_hlist_of_properties(
            lists=lists,
            properties=properties,
        )


if __name__ == "__main__":
    pytest.main([__file__])
