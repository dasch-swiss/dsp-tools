from unittest.mock import Mock

AUTH = Mock()
AUTH.get_token = Mock(return_value="test-token")

SERVER = "http://localhost:3333"
ONTO_IRI = "http://localhost:3333/ontology/0001/my-onto/v2"
CLASS_IRI = "http://localhost:3333/ontology/0001/my-onto/v2#Book"
