import pytest

from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.connection_live import ConnectionLive

class SessionMock:
    def post(self, url: str, data: bytes, *args, **kwargs) -> dict:
        if url == "http://0.0.0.0:3333/v2/authentication" and data == b'{"email":"root@example.com","password":"test"}':
            return {"token": "token"}


def test_log_in_and_out() -> None:
    con = ConnectionLive("http://0.0.0.0:3333")
    con.login("root@example.com", "test")
    assertIsNotNone(con.token)
    con.logout()
    assertIsNone(con.token)
    with assertRaises(UserError):
        con.login("invalid", "invalid")

def test_get() -> None:
    res = con.get("/ontology/0001/anything/simple/v2")
    assertIsNotNone(res["@graph"])
    assertRaises(BaseError, con.get, "/doesNotExist")
    con.logout()
    assertIsNotNone(res["@graph"])
    assertRaises(BaseError, con.get, "/doesNotExist")

def test_post() -> None:
    res_info = {
        "@type": "anything:Thing",
        "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
        "anything:hasBoolean": {"@type": "knora-api:BooleanValue", "knora-api:booleanValueAsBoolean": True},
        "rdfs:label": "knora-py thing",
        "knora-api:hasPermissions": "CR knora-admin:Creator|V http://rdfh.ch/groups/0001/thing-searcher",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "anything": "http://0.0.0.0:3333/ontology/0001/anything/v2#",
        },
    }

    res = con.post("/v2/resources", res_info)

    assertIsNotNone(res["@id"])
    assertEqual(res["@type"], "anything:Thing")
    assertEqual(res["rdfs:label"], "knora-py thing")

    res_id = res["@id"]

    erase_info = {
        "@id": f"{res_id}",
        "@type": "anything:Thing",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "anything": "http://0.0.0.0:3333/ontology/0001/anything/v2#",
        },
    }

    res = con.post("/v2/resources/erase", erase_info)
    assertIsNotNone(res["knora-api:result"])
    assertEqual(res["knora-api:result"], "Resource erased")


if __name__ == "__main__":
    pytest.main([__file__])
