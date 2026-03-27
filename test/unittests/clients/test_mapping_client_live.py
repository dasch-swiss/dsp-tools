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

