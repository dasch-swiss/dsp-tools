"""end to end tests for resource class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.permission import PermissionValue, Permissions
from knora.dsplib.models.resource import ResourceInstanceFactory
from knora.dsplib.models.sipi import Sipi
from knora.dsplib.models.value import KnoraStandoffXml, make_value


class TestResource(unittest.TestCase):

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_Resource_create(self) -> None:
        # make class factory for project anything. The factory creates classes that implement the CRUD methods
        # for the given resource classes

        factory = ResourceInstanceFactory(self.con, 'anything')

        # get a blue_thing resource class
        blue_thing = factory.get_resclass_type('anything:BlueThing')

        a_blue_thing = blue_thing(con=self.con,
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
                                      'anything:hasUri': 'http://test.com:65500/res'
                                  }).create()

        new_blue_thing = a_blue_thing.read()
        self.assertEqual(new_blue_thing.label, "BlueThing")
        self.assertEqual(new_blue_thing.value("anything:hasColor"), ['#ff0033', '#0077FF'])
        self.assertEqual(new_blue_thing.value("anything:hasInteger"), 42)
        self.assertEqual(new_blue_thing.value("anything:hasBoolean"), True)
        self.assertEqual(new_blue_thing.value("anything:hasDecimal"), 3.14159)
        self.assertEqual(new_blue_thing.value("anything:hasText"), "Dies ist ein einfacher Text")

        thing_picture = factory.get_resclass_type('anything:ThingPicture')
        sipi = Sipi('http://0.0.0.0:1024', self.con.get_token())
        img = sipi.upload_bitstream('testdata/bitstreams/TEMP11.TIF')
        file_ref = img['uploadedFiles'][0]['internalFilename']
        res_perm = Permissions({PermissionValue.M: ["knora-admin:UnknownUser", "knora-admin:KnownUser"],
                                PermissionValue.CR: ["knora-admin:Creator", "knora-admin:ProjectAdmin"]})

        resource_bitstream = {
            'value': 'testdata/bitstreams/TEMP11.TIF',
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

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == '__main__':
    unittest.main()
