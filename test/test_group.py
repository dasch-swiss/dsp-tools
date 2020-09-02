import unittest

from dsplib.models.connection import Connection
from dsplib.models.group import Group


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
        #self.assertEqual(len(groups), 2)

    def test_Group(self):
        """
        Test the creation of the group instance (without interaction with the triple store...)
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                      name="KNORA-PY-TEST",
                      description="Test project for knora-py",
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False)
        self.assertEqual(group.name, 'KNORA-PY-TEST')
        self.assertEqual(group.description, 'Test project for knora-py')
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
        self.assertEqual(group.description, 'A group for thing searchers.')
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
                           name="KNORA-PY CREATE",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False).create()
        self.iri = group.id

        self.assertEqual(group.name, 'KNORA-PY CREATE')
        self.assertEqual(group.description, 'Test project for knora-py')
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
                      name="KNORA-PY UPDATE",
                      description="Test project for knora-py",
                      project="http://rdfh.ch/projects/0001",
                      status=True,
                      selfjoin=False).create()
        self.iri = group.id
        group.name="KNORA-PY UPDATE - modified"
        group.description = "gaga gaga gaga gaga gaga gaga gaga"
        group.selfjoin = True
        group.status = False
        ngroup = group.update()
        self.assertEqual(group.name, 'KNORA-PY UPDATE - modified')
        self.assertEqual(group.description, 'gaga gaga gaga gaga gaga gaga gaga')
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
                           name="KNORA-PY DELETE",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False).create()
        self.iri = group.id
        ngroup = group.delete()
        self.assertEqual(ngroup.name, 'KNORA-PY DELETE')
        self.assertEqual(ngroup.description, 'Test project for knora-py')
        self.assertEqual(ngroup.project, 'http://rdfh.ch/projects/0001')
        self.assertFalse(ngroup.status)
        self.assertFalse(ngroup.selfjoin)


if __name__ == '__main__':
    unittest.main()
