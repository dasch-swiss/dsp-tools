import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group


class TestGroup(unittest.TestCase):
    iri = None

    def test_getAllGroups(self):
        """
        Test if we can retrieve all groups
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        groups = Group.getAllGroups(con)
        self.assertIsNotNone(groups)
        for group in groups:
            group.print()

    def test_Group(self):
        """
        Test the creation of the group instance (without interaction with the triple store...)
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      name="TEST GROUP",
                      descriptions={"en": "Test group"},
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False)
        self.assertEqual(group.name, 'TEST GROUP')
        self.assertCountEqual(group.descriptions.toJsonObj(), [{'language': 'en', 'value': 'Test group'}])
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertFalse(group.selfjoin)

    def test_Group_read(self):
        """
        Test if we can read an existing group and retrieve information about it
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      id='http://rdfh.ch/groups/0001/thing-searcher').read()
        self.assertEqual(group.name, 'Thing searcher')
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_create(self):
        """
        Test if we can create a new group in the triple store
        :return: None
        """
        global __iri
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      name="GROUP CREATE",
                      descriptions={"en": "Test group"},
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False).create()
        self.iri = group.id

        self.assertEqual(group.name, 'GROUP CREATE')
        self.assertCountEqual(group.descriptions.toJsonObj(), [{'language': 'en', 'value': 'Test group'}])
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertFalse(group.selfjoin)

    def test_Group_update(self):
        """
        Here we test if we can update an existing group
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      name="GROUP UPDATE",
                      descriptions={"en": "Test group"},
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False).create()
        self.iri = group.id
        group.name = "GROUP UPDATE - modified"
        group.descriptions = {"en": "Test group updated"}
        group.selfjoin = True
        group.status = False
        ngroup = group.update()
        self.assertEqual(group.name, 'GROUP UPDATE - modified')
        self.assertCountEqual(group.descriptions.toJsonObj(), [{'language': 'en', 'value': 'Test group updated'}])
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertFalse(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_delete(self):
        """
        Here we test if we can mark an existing group as deleted (it will not be deleted completely
        from the triplestore, but marked!!)
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      name="GROUP DELETE",
                      descriptions={"en": "Test group"},
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False).create()
        self.iri = group.id
        ngroup = group.delete()
        self.assertEqual(ngroup.name, 'GROUP DELETE')
        self.assertCountEqual(ngroup.descriptions.toJsonObj(), [{'language': 'en', 'value': 'Test group'}])
        self.assertEqual(ngroup.project, 'http://rdfh.ch/projects/0001')
        self.assertFalse(ngroup.status)
        self.assertFalse(ngroup.selfjoin)


if __name__ == '__main__':
    unittest.main()
