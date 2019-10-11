import unittest
from knora import Knora


class TestKnora(unittest.TestCase):

    def con(self, login: bool = True) -> Knora:
        server = "http://0.0.0.0:3333"
        email = "root@example.com"
        password = "test"
        # projectcode = "00FE"
        # ontoname = "KPT"
        con = Knora(server)
        if login:
            con.login(email, password)
        return con

    # resets the content of the triplestore
    def test_reset_triplestore_content(self):
        res = self.con(login=False).reset_triplestore_content()
        self.assertIsNotNone(res)

    # retrieves all users
    def test_get_users(self):
        res = self.con(login=True).get_users()
        # print(res)
        self.assertEqual(len(res), 19)

    # retrieves user information
    def test_get_user(self):
        res = self.con(login=True).get_user_by_iri(user_iri='http://rdfh.ch/users/root')
        # print(res)
        self.assertEqual(res["username"], "root")

    # creates a user
    def test_create_user(self):
        connection = self.con(login=True)
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

        # print(user_iri)

        # check that the created user exists
        res = connection.get_user_by_iri(user_iri)
        self.assertEqual(res["username"], "testtest")
        self.assertEqual(res["email"], "testtest@example.com")

        # logout current user
        connection.logout()
        self.assertIsNone(connection.get_token())

        # login as newly created user
        connection.login(res["email"], "test")
        self.assertIsNotNone(connection.get_token())


if __name__ == "__main__":
    unittest.main()
