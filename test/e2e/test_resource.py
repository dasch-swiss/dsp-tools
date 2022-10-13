"""end to end tests for resource class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.permission import PermissionValue, Permissions
from knora.dsplib.models.resource import ResourceInstanceFactory
from knora.dsplib.models.sipi import Sipi
from knora.dsplib.models.value import KnoraStandoffXml, make_value


class TestResource(unittest.TestCase):
    con = Connection('http://0.0.0.0:3333')

    @classmethod
    def setUpClass(cls) -> None:
        cls.con.login('root@example.com', 'test')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.con.logout()

    def test_resource_create(self) -> None:
        # make class factory for project anything. The factory creates classes that implement the CRUD methods
        # for the given resource classes

        factory = ResourceInstanceFactory(self.con, 'anything')

        # get a blue_thing resource class
        blue_thing = factory.get_resclass_type('anything:BlueThing')

        a_blue_thing = blue_thing(con=self.con,
                                  label='BlueThing',
                                  creation_date='1999-12-31T23:59:59.9999999+01:00',
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
                                      'anything:hasUri': 'http://test.com:65500/res'
                                  }).create()

        new_blue_thing = a_blue_thing.read()
        self.assertEqual(new_blue_thing.label, "BlueThing")
        self.assertEqual(new_blue_thing.value("anything:hasColor"), ['#ff0033', '#0077FF'])
        self.assertEqual(new_blue_thing.value("anything:hasInteger"), 42)
        self.assertEqual(new_blue_thing.value("anything:hasBoolean"), True)
        self.assertEqual(new_blue_thing.value("anything:hasDecimal"), 3.14159)
        self.assertEqual(new_blue_thing.value("anything:hasText"), "Dies ist ein einfacher Text")
        self.assertEqual(new_blue_thing.creation_date, "1999-12-31T23:59:59.9999999+01:00")

        thing_picture = factory.get_resclass_type('anything:ThingPicture')
        sipi = Sipi('http://0.0.0.0:1024', self.con.get_token())
        img = sipi.upload_bitstream('testdata/bitstreams/test.tif')
        file_ref = img['uploadedFiles'][0]['internalFilename']
        res_perm = Permissions({PermissionValue.M: ["knora-admin:UnknownUser", "knora-admin:KnownUser"],
                                PermissionValue.CR: ["knora-admin:Creator", "knora-admin:ProjectAdmin"]})

        resource_bitstream = {
            'value': 'testdata/bitstreams/test.tif',
            'internal_file_name': file_ref,
            'permissions': res_perm
        }

        thing_picture(
            con=self.con,
            label='ThingPicture',
            bitstream=resource_bitstream,
            permissions=res_perm,
            values={
                'anything:hasPictureTitle': make_value(value="A Thing Picture named Lena", permissions=res_perm)
            }
        ).create()


    def test_creation_date(self) -> None:
        factory = ResourceInstanceFactory(self.con, 'anything')
        blue_thing = factory.get_resclass_type('anything:BlueThing')
        invalid_timestamps = ["1999-12-32T23:59:59+01:00", "1999-12-31T25:59:59+01:00", "1999-12-31T25:59:59"]
        for invalid_timestamp in invalid_timestamps:
            with self.assertRaisesRegex(BaseError, "Invalid datatype value literal"):
                a_blue_thing = blue_thing(con=self.con,
                                          label='BlueThing',
                                          creation_date=invalid_timestamp,
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
                                              'anything:hasUri': 'http://test.com:65500/res'
                                          })
                a_blue_thing.create()


if __name__ == '__main__':
    unittest.main()
