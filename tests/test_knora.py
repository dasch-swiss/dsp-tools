import pytest
from knora import Knora

@pytest.fixture()
def con():
    def _con(login: bool = True):
        server = "http://0.0.0.0:3333"
        email = "root@example.com"
        password = "test"
        # projectcode = "00FE"
        # ontoname = "KPT"
        con = Knora(server)
        if (login):
            con.login(email, password)
        return con

    return _con


# resets the content of the triplestore
def test_reset_triplestore_content(con):
    res = con(False).reset_triplestore_content()
    assert(res)


# retrieves user information
def test_get_user(con):
    res = con(True).get_user("http://rdfh.ch/users/root")
    assert(res["username"] == "root")

# creates a user
def test_create_user(con):
    connection = con(True)
    user = {
        "username": "testtest",
        "email": "testtest@example.com",
        "givenName": "test_given",
        "familyName": "test_family",
        "password": "test",
        "lang": "en"
    }

    user_iri = connection.create_user(
        username=user["username"],
        email=user["email"],
        givenName=user["givenName"],
        familyName=user["familyName"],
        password=user["password"],
        lang=user["lang"] if user.get("lang") is not None else "en")

    print(user_iri)

    res = connection.get_user(user_iri)

    assert(res["username"] == "testtest")
    assert(res["email"] == "testtest@example.com")

    # try to login
    connection.logout()
    connection.login(res["email"], "test")
