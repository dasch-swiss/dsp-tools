import pytest
from knora import Knora


@pytest.fixture()
def con():
    def _con(login: bool = True) -> Knora:
        server = "http://0.0.0.0:3333"
        email = "root@example.com"
        password = "test"
        # projectcode = "00FE"
        # ontoname = "KPT"
        con = Knora(server)
        if login:
            con.login(email, password)
        return con

    return _con


# resets the content of the triplestore
def test_reset_triplestore_content(con):
    res = con(login=False).reset_triplestore_content()
    assert res


# retrieves all users
def test_get_users(con):
    res = con(login=True).get_users()
    print(res)
    assert (len(res) == 18)


# retrieves user information
def test_get_user(con):
    res = con(login=True).get_user_by_iri(user_iri='http://rdfh.ch/users/root')
    print(res)
    assert (res["username"] == "root")


# creates a user
def test_create_user(con):
    connection = con(login=True)
    user = {
        "username": "testtest",
        "email": "testtest@example.com",
        "given_name": "test_given",
        "family_name": "test_family",
        "password": "test",
        "lang": "en"
    }

    user_iri = connection.create_user(
        username=user["username"],
        email=user["email"],
        given_name=user["given_name"],
        family_name=user["family_name"],
        password=user["password"],
        lang=user["lang"] if user.get("lang") is not None else "en")

    print(user_iri)

    res = connection.get_user_by_iri(user_iri)

    assert (res["username"] == "testtest")
    assert (res["email"] == "testtest@example.com")

    # try to login
    connection.logout()
    connection.login(res["email"], "test")
