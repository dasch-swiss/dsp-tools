import unittest
from pprint import pprint
from knora import Knora, Sipi


class TestCreateResource(unittest.TestCase):

    @unittest.skip("not implemented")
    def test_create_resource(self):
        server = "http://0.0.0.0:3333"
        sipi = "http://0.0.0.0:1024"
        email = "root@example.com"
        password = "test"
        projectcode = "00FE"
        ontoname = "KPT"

        con = Knora(server)
        con.login(email, password)
        graph = con.get_ontology_graph('00FE', 'knora-py-test')
        # print(graph)
        # exit(0)
        schema = con.create_schema(projectcode, ontoname)
        # pprint(schema)
        # exit(0)

        inst1_info = con.create_resource(schema, "MyObject", "obj_inst1", {
            "mySimpleText": "Dies ist ein Text!",
            "myRichText": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<text><p><strong>this is</strong> text</p> with standoff</text>",
            "myColor": "#ff7700",
            "myDate": "1966:CE:1967-05-21",
            "myDecimal": {'value': "3.14159", 'comment': "Die Zahl PI"},
            "myGeoname": "2661604",
            "myList": "options:opt2",
            "myInteger": 7,
            "myInterval": "13.57:15.88",
            "myTime": "2019-10-23T13.45:12Z",
            "myBoolean": "true"
        })
        pprint(inst1_info)

        # first upload image to SIPI
        sipi = Sipi(sipi, con.get_token())
        res = sipi.upload_image('test.tif')
        pprint(res)

        fileref = res['uploadedFiles'][0]['internalFilename']
        inst2_info = con.create_resource(schema, "MyImage", "image_inst1", {
            "titleprop": "Stained glass",
            "linkprop": inst1_info['iri']
        }, fileref)
        pprint(inst2_info)


if __name__ == "__main__":
    unittest.main()
