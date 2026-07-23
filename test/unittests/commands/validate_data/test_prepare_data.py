import pytest

from dsp_tools.clients.list_client import ListInfo
from dsp_tools.commands.validate_data.prepare_data.prepare_data import _format_metadata_export
from dsp_tools.commands.validate_data.prepare_data.prepare_data import _reformat_one_list

PROJECT_IRI = "http://rdfh.ch/projects/projectIRI"


@pytest.fixture
def response_one_list() -> ListInfo:
    return ListInfo(
        {
            "id": "http://rdfh.ch/lists/9999/list1",
            "projectIri": PROJECT_IRI,
            "name": "firstList",
            "labels": [{"value": "List 1", "language": "en"}],
            "comments": [{"value": "This is the first list", "language": "en"}],
            "isRootNode": True,
        },
        [
            {
                "id": "http://rdfh.ch/lists/9999/n1",
                "name": "n1",
                "labels": [{"value": "Node 1", "language": "en"}],
                "comments": [],
                "position": 0,
                "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                "children": [
                    {
                        "id": "http://rdfh.ch/lists/9999/n11",
                        "name": "n1.1",
                        "labels": [{"value": "Node 1.1", "language": "en"}],
                        "comments": [],
                        "position": 0,
                        "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                        "children": [
                            {
                                "id": "http://rdfh.ch/lists/9999/n111",
                                "name": "n1.1.1",
                                "labels": [{"value": "Node 1.1.1", "language": "en"}],
                                "comments": [],
                                "position": 0,
                                "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                "children": [],
                            },
                            {
                                "id": "http://rdfh.ch/lists/9999/n112",
                                "name": "n1.1.2",
                                "labels": [{"value": "Node 1.1.2", "language": "en"}],
                                "comments": [],
                                "position": 1,
                                "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                "children": [],
                            },
                        ],
                    }
                ],
            }
        ],
    )


def test_reformat_one_list(response_one_list) -> None:
    result = _reformat_one_list(response_one_list)
    sorted_nodes = sorted(result.nodes, key=lambda x: x.name)
    assert result.list_iri == "http://rdfh.ch/lists/9999/list1"
    assert result.list_name == "firstList"
    names = [x.name for x in sorted_nodes]
    assert names == ["n1", "n1.1", "n1.1.1", "n1.1.2"]
    expected_iris = [
        "http://rdfh.ch/lists/9999/n1",
        "http://rdfh.ch/lists/9999/n11",
        "http://rdfh.ch/lists/9999/n111",
        "http://rdfh.ch/lists/9999/n112",
    ]
    iris = [x.iri for x in sorted_nodes]
    assert iris == expected_iris


class TestReformatMetadata:
    def test_no_metadata(self):
        inpt_metadata: list[dict[str, str | None]] = []
        result = _format_metadata_export(inpt_metadata)
        assert len(result) == 0

    def test_deleted_column_not_existing(self):
        inpt_metadata: list[dict[str, str | None]] = [{"resourceIri": "iri_1", "resourceClassIri": "res_1"}]
        result = _format_metadata_export(inpt_metadata)
        result_ids = {x.res_iri for x in result}
        expected_ids = {"iri_1"}
        assert result_ids == expected_ids

    def test_none_deleted(self):
        inpt_metadata = [
            {"resourceIri": "iri_1", "resourceClassIri": "res_1", "Deletion Date (if available)": None},
            {"resourceIri": "iri_2", "resourceClassIri": "res_2", "Deletion Date (if available)": None},
        ]
        result = _format_metadata_export(inpt_metadata)
        result_ids = {x.res_iri for x in result}
        expected_ids = {"iri_1", "iri_2"}
        assert result_ids == expected_ids

    def test_some_deleted(self):
        inpt_metadata: list[dict[str, str | None]] = [
            {"resourceIri": "iri_1", "resourceClassIri": "res_1", "Deletion Date (if available)": "today"},
            {"resourceIri": "iri_2", "resourceClassIri": "res_2", "Deletion Date (if available)": None},
        ]
        result = _format_metadata_export(inpt_metadata)
        result_ids = {x.res_iri for x in result}
        expected_ids = {"iri_2"}
        assert result_ids == expected_ids
