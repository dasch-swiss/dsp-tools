import unittest

from dsplib.models.connection import Connection
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.value import BooleanValue, ColorValue, DateValue, DecimalValue, IntValue, IntervalValue, TextValue, \
    UriValue, KnoraStandoffXml, make_value
from dsplib.models.permission import PermissionValue, Permissions, PermissionsIterator
from dsplib.models.sipi import Sipi

from pprint import pprint

class TestResource(unittest.TestCase):

    def test_Resource_create(self):
        #
        # Connect to Knora
        #
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        #
        # Make class factory for project 'anything. The factory creates classes that implement the CRUD methods
        # for the given resource classes, that is to create, read, update and delete instances (=resources) of the given classesd
        #
        factory = ResourceInstanceFactory(con, 'anything')
        resclassnames = factory.get_resclass_names()

        #
        # Get an python class of a BlueThing resource class
        #
        BlueThing = factory.get_resclass('anything:BlueThing')

        an_old_thing = BlueThing(con=con, iri="http://rdfh.ch/0001/H6gBWUuJSuuO-CilHV8kQw").read()

        a_blue_thing = BlueThing(con=con,
                                 label='BlueThing',
                                 values={
                                     'anything:hasBoolean': True,
                                     'anything:hasColor': ['#ff0033', '#0077FF'],
                                     'anything:hasDate': make_value(value='1833', comment='not verified!'),
                                     'anything:hasDecimal': 3.14159,
                                     'anything:hasInteger': "42",
                                     'anything:hasTimeStamp': "2004-04-12T13:20:00Z",
                                     'anything:hasInterval': [make_value(value="0.0:3.0", comment="first interval"),
                                                              make_value(value="3.5:3.7", comment="second interval")],
                                     'anything:hasRichtext': KnoraStandoffXml("This is <em>bold</em> text."),
                                     'anything:hasText': "Dies ist ein einfacher Text",
                                     'anything:hasUri': 'http://gaga.com:65500/gugus'
                                 }).create()


        new_blue_thing = a_blue_thing.read()
        self.assertEqual(a_blue_thing.label, "BlueThing")
        self.assertEqual(a_blue_thing.value("anything:hasColor"), ['#ff0033', '#0077FF'])
        self.assertEqual(a_blue_thing.value("anything:hasInteger"), 42)
        self.assertEqual(a_blue_thing.value("anything:hasBoolean"), True)
        self.assertEqual(a_blue_thing.value("anything:hasDecimal"), 3.14159)
        self.assertEqual(a_blue_thing.value("anything:hasText"), "Dies ist ein einfacher Text")

        ThingPicture = factory.get_resclass('anything:ThingPicture')
        sipi = Sipi('http://0.0.0.0:1024', con.get_token())
        img = sipi.upload_bitstream('testdata/bitstreams/TEMP11.TIF')
        fileref = img['uploadedFiles'][0]['internalFilename']
        resperm = Permissions({PermissionValue.M: ["knora-admin:UnknownUser", "knora-admin:KnownUser"],
                       PermissionValue.CR: ["knora-admin:Creator", "knora-admin:ProjectAdmin"]})
        a_thing_picture = ThingPicture(
            con=con,
            label='ThingPicture',
            bitstream=fileref,
            permissions=resperm,
            values={
                'anything:hasPictureTitle': make_value(value="A Thing Picture named Lena", permissions=resperm)
            }
        ).create()


if __name__ == '__main__':
    unittest.main()
