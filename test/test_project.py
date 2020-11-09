import unittest

from dsplib.models.connection import Connection
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.project import Project


class TestProject(unittest.TestCase):

    def test_project(self):
        con = Connection('http://0.0.0.0:3333')
        project = Project(
            con=con,
            id='http://rdfh.ch/gaga',
            shortcode='0FF0',
            shortname="pytest",
            longname="Python testing",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        )
        self.assertIsNotNone(project)
        self.assertEqual(project.id, 'http://rdfh.ch/gaga')
        self.assertEqual(project.shortcode, '0FF0')
        self.assertEqual(project.shortname, 'pytest')
        self.assertEqual(project.longname, 'Python testing')
        self.assertEqual(project.description['en'], 'knora-py testing')
        self.assertEqual(project.description['de'], 'Tests für knora-py')
        self.assertEqual(project.selfjoin, False)
        self.assertEqual(project.status, True)
        self.assertEqual(project.keywords, {'test', 'testing', 'gaga'})
        self.assertEqual(project.logo, 'gaga.gif')

    def test_read(self):
        con = Connection('http://0.0.0.0:3333')
        project = Project(
            con=con,
            id='http://rdfh.ch/projects/0001'
        ).read()
        self.assertIsNotNone(project)
        self.assertEqual(project.id, 'http://rdfh.ch/projects/0001')
        self.assertEqual(project.shortcode, '0001')
        self.assertEqual(project.shortname, 'anything')
        self.assertEqual(project.longname, 'Anything Project')
        self.assertEqual(project.description[None], 'Anything Project')
        self.assertEqual(project.selfjoin, False)
        self.assertEqual(project.status, True)

    def test_create(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = Project(
            con=con,
            shortcode='0FF0',
            shortname="pytest0",
            longname="Python testing 0",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        )
        nproject = project.create()
        self.assertIsNotNone(nproject)
        self.assertEqual(nproject.shortcode, '0FF0')
        self.assertEqual(nproject.shortname, 'pytest0')
        self.assertEqual(nproject.longname, 'Python testing 0')
        self.assertEqual(nproject.description['en'], 'knora-py testing')
        self.assertEqual(nproject.description['de'], 'Tests für knora-py')
        self.assertEqual(nproject.selfjoin, False)
        self.assertEqual(nproject.status, True)
        self.assertEqual(nproject.keywords, {'test', 'testing', 'gaga'})

    def test_update(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = Project(
            con=con,
            shortcode='0FF1',
            shortname="pytest1",
            longname="Python testing 1",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        ).create()

        project.shortname = "pytest1a"
        project.longname = "Python testing 1a"
        project.addDescription('fr', 'Les testes pour python')
        project.rmDescription('de')
        project.selfjoin = True
        project.status = False
        project.rmKeyword('gaga')
        project.addKeyword('Guguseli')
        nproject = project.update()

        self.assertIsNotNone(nproject)
        self.assertEqual(nproject.shortcode, '0FF1')
        # self.assertEqual(nnproject.shortname, 'pytest2') # Does not work....? Knora-API problem
        self.assertEqual(nproject.longname, 'Python testing 1a')
        self.assertEqual(nproject.description['en'], 'knora-py testing')
        self.assertEqual(nproject.description['fr'], 'Les testes pour python')
        self.assertEqual(nproject.selfjoin, True)
        self.assertEqual(nproject.status, False)
        self.assertEqual(nproject.keywords, {'test', 'testing', 'Guguseli'})

    def test_delete(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = Project(
            con=con,
            shortcode='0FF2',
            shortname="pytest2",
            longname="Python testing 2",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        ).create()

        nproject = project.delete()
        self.assertIsNotNone(nproject)
        self.assertEqual(nproject.shortcode, '0FF2')
        self.assertEqual(nproject.shortname, 'pytest2')
        self.assertEqual(nproject.longname, 'Python testing 2')
        self.assertEqual(nproject.description['en'], 'knora-py testing')
        self.assertEqual(nproject.description['de'], 'Tests für knora-py')
        self.assertEqual(nproject.selfjoin, False)
        self.assertEqual(nproject.status, False)
        self.assertEqual(nproject.keywords, {'test', 'testing', 'gaga'})

if __name__ == '__main__':
    unittest.main()
