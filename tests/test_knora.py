import pytest
from knora import Knora

@pytest.fixture()
def con():
    server = "http://0.0.0.0:3333"
    email = "root@example.com"
    password = "test"
    # projectcode = "00FE"
    # ontoname = "KPT"

    con = Knora(server, email, password)
    return con

def test_reset_triplestore_content(con):
    res = con.reset_triplestore_content
    assert(res == "gaga")

def test_get_user(con):
    res = con.get_user("http://rdfh.ch/users/root")
    assert(res["username"] == "root")

def test_create_user(con):
    user = {
        "username": "testtest",
        "email": "testtest@example.com",
        "givenName": "test_given",
        "familyName": "test_family",
        "password": "test",
        "lang": "en"
    }

    user_iri = con.create_user(
        username=user["username"],
        email=user["email"],
        givenName=user["givenName"],
        familyName=user["familyName"],
        password="password",
        lang=user["lang"] if user.get("lang") is not None else "en")

    res = con.get_user(user_iri)

    assert(res["username"] == "testtest")
    assert(res["email"] == "testtest@example.com")
