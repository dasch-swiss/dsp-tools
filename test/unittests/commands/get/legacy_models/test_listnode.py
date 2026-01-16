from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.get.legacy_models.listnode import ListNode
from dsp_tools.commands.get.legacy_models.listnode import create_list_node_from_json
from dsp_tools.commands.get.legacy_models.listnode import get_all_lists
from dsp_tools.commands.get.legacy_models.listnode import read_all_nodes
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import create_lang_string


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


class TestCreateListNodeFromJson:
    """Tests for the create_list_node_from_json factory function."""

    def test_missing_id_raises(self, mock_connection: Mock) -> None:
        json_obj: dict[str, Any] = {"name": "node", "labels": []}
        with pytest.raises(BaseError, match="id is missing"):
            create_list_node_from_json(mock_connection, json_obj)

    def test_missing_name_uses_iri_suffix(self, mock_connection: Mock) -> None:
        # Fallback logic: when name is missing, extract from IRI
        json_obj = {
            "id": "http://rdfh.ch/lists/0001/mylist-node",
            "labels": [{"language": "en", "value": "Node Label"}],
        }
        node = create_list_node_from_json(mock_connection, json_obj)
        assert node.name == "mylist-node"

    def test_node_without_children(self, mock_connection: Mock) -> None:
        json_obj = {
            "id": "http://rdfh.ch/lists/0001/node",
            "name": "testnode",
            "labels": [{"language": "en", "value": "Test Node"}],
        }
        node = create_list_node_from_json(mock_connection, json_obj)
        assert node.children == ()

    def test_node_with_children(self, mock_connection: Mock) -> None:
        # Recursive structure handling
        json_obj = {
            "id": "http://rdfh.ch/lists/0001/parent",
            "name": "parent",
            "labels": [{"language": "en", "value": "Parent"}],
            "children": [
                {
                    "id": "http://rdfh.ch/lists/0001/child",
                    "name": "child",
                    "labels": [{"language": "en", "value": "Child"}],
                }
            ],
        }
        node = create_list_node_from_json(mock_connection, json_obj)
        assert len(node.children) == 1
        assert node.children[0].name == "child"

    def test_project_iri_passed_to_children(self, mock_connection: Mock) -> None:
        # Project IRI should propagate to children
        json_obj = {
            "id": "http://rdfh.ch/lists/0001/parent",
            "name": "parent",
            "labels": [],
            "children": [
                {
                    "id": "http://rdfh.ch/lists/0001/child",
                    "name": "child",
                    "labels": [],
                }
            ],
        }
        node = create_list_node_from_json(mock_connection, json_obj, project_iri="http://rdfh.ch/projects/0001")
        assert node.children[0].project == "http://rdfh.ch/projects/0001"


class TestListNodeToDefinitionFileObj:
    """Tests for ListNode.to_definition_file_obj serialization."""

    def test_without_children(self) -> None:
        node = ListNode(
            iri="http://rdfh.ch/lists/0001/node",
            name="testnode",
            project=None,
            label=create_lang_string({"en": "Test Node"}),
            comments=create_lang_string(),
            children=(),
        )
        result = node.to_definition_file_obj()
        assert "nodes" not in result  # Key omitted when no children
        assert result["name"] == "testnode"
        assert "labels" in result

    def test_with_children(self) -> None:
        child = ListNode(
            iri="http://rdfh.ch/lists/0001/child",
            name="child",
            project=None,
            label=create_lang_string({"en": "Child"}),
            comments=create_lang_string(),
            children=(),
        )
        parent = ListNode(
            iri="http://rdfh.ch/lists/0001/parent",
            name="parent",
            project=None,
            label=create_lang_string({"en": "Parent"}),
            comments=create_lang_string(),
            children=(child,),
        )
        result = parent.to_definition_file_obj()
        assert "nodes" in result  # Key present when children exist
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "child"

    def test_with_comments(self) -> None:
        node = ListNode(
            iri="http://rdfh.ch/lists/0001/node",
            name="testnode",
            project=None,
            label=create_lang_string({"en": "Test Node"}),
            comments=create_lang_string({"en": "A comment"}),
            children=(),
        )
        result = node.to_definition_file_obj()
        assert "comments" in result

    def test_without_comments(self) -> None:
        # Empty comments should not be included
        node = ListNode(
            iri="http://rdfh.ch/lists/0001/node",
            name="testnode",
            project=None,
            label=create_lang_string({"en": "Test Node"}),
            comments=create_lang_string(),
            children=(),
        )
        result = node.to_definition_file_obj()
        assert "comments" not in result

    def test_nested_children_serialization(self) -> None:
        # Verify recursive serialization works
        grandchild = ListNode(
            iri="http://rdfh.ch/lists/0001/grandchild",
            name="grandchild",
            project=None,
            label=create_lang_string({"en": "Grandchild"}),
            comments=create_lang_string(),
            children=(),
        )
        child = ListNode(
            iri="http://rdfh.ch/lists/0001/child",
            name="child",
            project=None,
            label=create_lang_string({"en": "Child"}),
            comments=create_lang_string(),
            children=(grandchild,),
        )
        parent = ListNode(
            iri="http://rdfh.ch/lists/0001/parent",
            name="parent",
            project=None,
            label=create_lang_string({"en": "Parent"}),
            comments=create_lang_string(),
            children=(child,),
        )
        result = parent.to_definition_file_obj()
        assert result["nodes"][0]["nodes"][0]["name"] == "grandchild"


class TestGetAllLists:
    """Tests for the get_all_lists API function."""

    def test_without_project_iri(self, mock_connection: Mock) -> None:
        # Uses base route when no project IRI provided
        mock_connection.get.return_value = {
            "lists": [
                {"id": "http://rdfh.ch/lists/0001/list1", "labels": []},
            ]
        }
        result = get_all_lists(mock_connection)
        mock_connection.get.assert_called_once_with("/admin/lists")
        assert len(result) == 1

    def test_with_project_iri(self, mock_connection: Mock) -> None:
        # Appends project IRI as URL parameter when provided
        mock_connection.get.return_value = {
            "lists": [
                {"id": "http://rdfh.ch/lists/0001/list1", "labels": []},
            ]
        }
        result = get_all_lists(mock_connection, "http://rdfh.ch/projects/0001")
        mock_connection.get.assert_called_once_with("/admin/lists?projectIri=http%3A%2F%2Frdfh.ch%2Fprojects%2F0001")
        assert len(result) == 1

    def test_missing_lists_key_raises(self, mock_connection: Mock) -> None:
        # Error when "lists" key is missing from response
        mock_connection.get.return_value = {"other_key": []}
        with pytest.raises(BaseError, match="Request got no lists!"):
            get_all_lists(mock_connection)

    def test_returns_multiple_lists(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {
            "lists": [
                {"id": "http://rdfh.ch/lists/0001/list1", "name": "list1", "labels": []},
                {"id": "http://rdfh.ch/lists/0001/list2", "name": "list2", "labels": []},
            ]
        }
        result = get_all_lists(mock_connection)
        assert len(result) == 2
        assert result[0].name == "list1"
        assert result[1].name == "list2"


class TestReadAllNodes:
    """Tests for the read_all_nodes API function."""

    def test_missing_list_key_raises(self, mock_connection: Mock) -> None:
        # First error condition: "list" key missing
        mock_connection.get.return_value = {"other_key": {}}
        with pytest.raises(BaseError, match="Request got no list!"):
            read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/mylist")

    def test_missing_listinfo_key_raises(self, mock_connection: Mock) -> None:
        # Second error condition: "listinfo" key missing from list
        mock_connection.get.return_value = {"list": {"other_key": {}}}
        with pytest.raises(BaseError, match="Request got no proper list information!"):
            read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/mylist")

    def test_valid_response_creates_listnode(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {
            "list": {
                "listinfo": {
                    "id": "http://rdfh.ch/lists/0001/mylist",
                    "name": "mylist",
                    "labels": [{"language": "en", "value": "My List"}],
                },
            }
        }
        result = read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/mylist")
        assert result.name == "mylist"
        assert result.iri == "http://rdfh.ch/lists/0001/mylist"

    def test_missing_name_uses_iri_suffix(self, mock_connection: Mock) -> None:
        # Fallback logic when name is missing
        mock_connection.get.return_value = {
            "list": {
                "listinfo": {
                    "id": "http://rdfh.ch/lists/0001/mylist-node",
                    "labels": [],
                },
            }
        }
        result = read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/mylist-node")
        assert result.name == "mylist-node"

    def test_with_children(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {
            "list": {
                "listinfo": {
                    "id": "http://rdfh.ch/lists/0001/root",
                    "name": "root",
                    "labels": [],
                    "projectIri": "http://rdfh.ch/projects/0001",
                },
                "children": [
                    {
                        "id": "http://rdfh.ch/lists/0001/child",
                        "name": "child",
                        "labels": [],
                    }
                ],
            }
        }
        result = read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/root")
        assert len(result.children) == 1
        assert result.children[0].name == "child"

    def test_uses_correct_route_with_encoded_iri(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {
            "list": {
                "listinfo": {
                    "id": "http://rdfh.ch/lists/0001/mylist",
                    "labels": [],
                },
            }
        }
        read_all_nodes(mock_connection, "http://rdfh.ch/lists/0001/mylist")
        mock_connection.get.assert_called_once_with("/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F0001%2Fmylist")
