import unittest
import pprint
import requests
from urllib.parse import quote_plus

from context import BaseError, Languages, Actions, LangString
from context import KnoraProject, KnoraConnection

def erase_project():
    sparql = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX knora-base: <http://www.knora.org/ontology/knora-base#>
        DELETE {
            GRAPH <http://www.knora.org/data/admin> {
                <http://rdfh.ch/projects/0FF0> ?property ?value
            }
        } WHERE {
            GRAPH <http://www.knora.org/data/admin> {
                <http://rdfh.ch/projects/0FF0> ?property ?value
            }
        }

    """
    req = requests.post('http://localhost:7200/repositories/knora-test/statements',
                        headers={'Content-Type': 'application/sparql-update',
                                 'Accept': 'application/json, text/plain, */*'},
                        data=sparql)
    if 'error' in req:
        print('ERROR: ' + req.error)
    if req.status_code != 204:
        print('STATUS-CODE: ' + str(req.status_code))
        print('TEXT: ' + req.text)
    return req.status_code

class TestKnoraProject(unittest.TestCase):


    def tearDown(self):
        res = erase_project()

    def test_KnoraProject(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        project = KnoraProject(
            con=con,
            id='http://rdfch/gaga',
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
        self.assertEqual(project.id, 'http://rdfch/gaga')
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
        con = KnoraConnection('http://0.0.0.0:3333')
        project = KnoraProject(
            con=con,
            id='http://rdfh.ch/projects/0001'
        )
        nproject = project.read()
        self.assertIsNotNone(nproject)
        self.assertEqual(nproject.id, 'http://rdfh.ch/projects/0001')
        self.assertEqual(nproject.shortcode, '0001')
        self.assertEqual(nproject.shortname, 'anything')
        self.assertEqual(nproject.longname, 'Anything Project')
        self.assertEqual(nproject.description['en'], 'Anything Project is a testing project ')
        self.assertEqual(nproject.selfjoin, False)
        self.assertEqual(nproject.status, False)
        self.assertEqual(nproject.keywords, {'test', 'dasch', 'anything'})

    def test_create(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = KnoraProject(
            con=con,
            shortcode='0FF0',
            shortname="pytest",
            longname="Python testing",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        )
        nproject = project.create()
        self.assertIsNotNone(nproject)
        self.assertEqual(nproject.shortcode, '0FF0')
        self.assertEqual(nproject.shortname, 'pytest')
        self.assertEqual(nproject.longname, 'Python testing')
        self.assertEqual(nproject.description['en'], 'knora-py testing')
        self.assertEqual(nproject.description['de'], 'Tests für knora-py')
        self.assertEqual(nproject.selfjoin, False)
        self.assertEqual(nproject.status, True)
        self.assertEqual(nproject.keywords, {'test', 'testing', 'gaga'})

    def test_update(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = KnoraProject(
            con=con,
            shortcode='0FF0',
            shortname="pytest",
            longname="Python testing",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        )
        nproject = project.create()

        nproject.shortname = "pytest2"
        nproject.longname = "Python testing no. 2"
        nproject.addDescription('fr', 'Les testes pour python')
        nproject.rmDescription('de')
        nproject.selfjoin = True
        nproject.status = False
        nproject.rmKeyword('gaga')
        nproject.addKeyword('Guguseli')
        nnproject = nproject.update()

        self.assertIsNotNone(nnproject)
        self.assertEqual(nnproject.shortcode, '0FF0')
        #self.assertEqual(nnproject.shortname, 'pytest2') # Does not work....? Knora-API problem
        self.assertEqual(nnproject.longname, 'Python testing no. 2')
        self.assertEqual(nnproject.description['en'], 'knora-py testing')
        self.assertEqual(nnproject.description['fr'], 'Les testes pour python')
        self.assertEqual(nnproject.selfjoin, True)
        self.assertEqual(nnproject.status, False)
        self.assertEqual(nnproject.keywords, {'test', 'testing', 'Guguseli'})

    def test_delete(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        project = KnoraProject(
            con=con,
            shortcode='0FF0',
            shortname="pytest",
            longname="Python testing",
            description=LangString({Languages.EN: 'knora-py testing', Languages.DE: 'Tests für knora-py'}),
            keywords={'test', 'testing', 'gaga'},
            selfjoin=False,
            status=True,
            logo='gaga.gif'
        )
        nproject = project.create()

        nnproject = nproject.delete()
        self.assertIsNotNone(nnproject)
        self.assertEqual(nnproject.shortcode, '0FF0')
        self.assertEqual(nnproject.shortname, 'pytest')
        self.assertEqual(nnproject.longname, 'Python testing')
        self.assertEqual(nnproject.description['en'], 'knora-py testing')
        self.assertEqual(nnproject.description['de'], 'Tests für knora-py')
        self.assertEqual(nnproject.selfjoin, False)
        self.assertEqual(nnproject.status, False)
        self.assertEqual(nnproject.keywords, {'test', 'testing', 'gaga'})

if __name__ == '__main__':
    unittest.main()
