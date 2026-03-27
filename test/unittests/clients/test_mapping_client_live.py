from unittest.mock import Mock
from urllib.parse import quote

import pytest
from requests_mock import Mocker

from dsp_tools.clients.exceptions import InvalidInputError
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import ResponseCodeAndText

AUTH = Mock()
AUTH.get_token = Mock(return_value="test-token")

SERVER = "http://localhost:3333"
ONTO_IRI = "http://localhost:3333/ontology/0001/my-onto/v2"
CLASS_IRI = "http://localhost:3333/ontology/0001/my-onto/v2#Book"


def _make_client() -> MappingClientLive:
    return MappingClientLive(server=SERVER, auth=AUTH)


def _class_url(onto_iri: str, class_iri: str) -> str:
    encoded_onto = quote(onto_iri, safe="")
    encoded_class = quote(class_iri, safe="")
    return f"{SERVER}/v3/ontologies/{encoded_onto}/classes/{encoded_class}/mapping"


def test_add_class_mapping_success(requests_mock: Mocker) -> None:
    requests_mock.put(_class_url(ONTO_IRI, CLASS_IRI), status_code=200)
    result = _make_client().put_class_mapping(ONTO_IRI, CLASS_IRI, ["http://schema.org/Book"])
    assert result == CLASS_IRI


def test_add_class_mapping_404_returned(requests_mock: Mocker) -> None:
    requests_mock.put(_class_url(ONTO_IRI, CLASS_IRI), status_code=404, text="not found")
    result = _make_client().put_class_mapping(ONTO_IRI, CLASS_IRI, ["http://schema.org/Book"])
    assert isinstance(result, ResponseCodeAndText)
    assert result.status_code == 404


def test_add_class_mapping_403_raises_bad_credentials(requests_mock: Mocker) -> None:
    requests_mock.put(_class_url(ONTO_IRI, CLASS_IRI), status_code=403)
    with pytest.raises(BadCredentialsError):
        _make_client().put_class_mapping(ONTO_IRI, CLASS_IRI, ["http://schema.org/Book"])


def test_add_class_mapping_400_raises_invalid_input(requests_mock: Mocker) -> None:
    requests_mock.put(_class_url(ONTO_IRI, CLASS_IRI), status_code=400, text="bad IRI")
    with pytest.raises(InvalidInputError):
        _make_client().put_class_mapping(ONTO_IRI, CLASS_IRI, ["not-an-iri"])


def test_iri_encoding_in_url_path(requests_mock: Mocker) -> None:
    onto = "http://localhost:3333/ontology/0001/my-onto/v2"
    cls = "http://localhost:3333/ontology/0001/my-onto/v2#Book"
    adapter = requests_mock.put(_class_url(onto, cls), status_code=200)
    _make_client().put_class_mapping(onto, cls, ["http://schema.org/Book"])
    assert adapter.called
    assert adapter.last_request is not None
    assert "%" in adapter.last_request.url
