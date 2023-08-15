"""end to end tests for resource class"""

# pylint: disable=missing-class-docstring,missing-function-docstring

from typing import cast
import unittest

import pytest

from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import DateTimeStamp
from dsp_tools.models.permission import Permissions, PermissionValue
from dsp_tools.models.resource import ResourceInstanceFactory
from dsp_tools.models.sipi import Sipi
from dsp_tools.models.value import KnoraStandoffXml, make_value


class TestResource(unittest.TestCase):
    con = Connection(server="http://0.0.0.0:3333", user_email="root@example.com", password="test")

    def test_resource_create(self) -> None:
        # make class factory for project anything. The factory creates classes that implement the CRUD methods
        # for the given resource classes

        factory = ResourceInstanceFactory(self.con, "anything")

        # get a blue_thing resource class
        blue_thing = factory.get_resclass_type("anything:BlueThing")

        a_blue_thing = blue_thing(
            con=self.con,
            label="BlueThing",
            creation_date=DateTimeStamp("1999-12-31T23:59:59.9999999+01:00"),
            values={
                "anything:hasBoolean": True,
                "anything:hasColor": ["#ff0033", "#0077FF"],
                "anything:hasDate": make_value(value="1833", comment="not verified!"),
                "anything:hasDecimal": 3.14159,
                "anything:hasInteger": "42",
                "anything:hasTimeStamp": "2004-04-12T13:20:00Z",
                "anything:hasInterval": [
                    make_value(value="0.0:3.0", comment="first interval"),
                    make_value(value="3.5:3.7", comment="second interval"),
                ],
                "anything:hasRichtext": KnoraStandoffXml("This is <em>bold</em> text."),
                "anything:hasText": "Dies ist ein einfacher Text",
                "anything:hasUri": "http://test.com:65500/res",
            },
        ).create()

        new_blue_thing = a_blue_thing.read()
        self.assertEqual(new_blue_thing.label, "BlueThing")
        self.assertEqual(new_blue_thing.value("anything:hasColor"), ["#ff0033", "#0077FF"])
        self.assertEqual(new_blue_thing.value("anything:hasInteger"), 42)
        self.assertEqual(new_blue_thing.value("anything:hasBoolean"), True)
        self.assertEqual(new_blue_thing.value("anything:hasDecimal"), 3.14159)
        self.assertEqual(new_blue_thing.value("anything:hasText"), "Dies ist ein einfacher Text")
        self.assertEqual(new_blue_thing.creation_date, DateTimeStamp("1999-12-31T23:59:59.9999999+01:00"))

        thing_picture = factory.get_resclass_type("anything:ThingPicture")
        sipi = Sipi("http://0.0.0.0:1024", cast(str, self.con.token))
        img = sipi.upload_bitstream("testdata/bitstreams/test.tif")
        file_ref = img["uploadedFiles"][0]["internalFilename"]
        res_perm = Permissions(
            {
                PermissionValue.M: ["knora-admin:UnknownUser", "knora-admin:KnownUser"],
                PermissionValue.CR: ["knora-admin:Creator", "knora-admin:ProjectAdmin"],
            }
        )

        resource_bitstream = {
            "value": "testdata/bitstreams/test.tif",
            "internal_file_name": file_ref,
            "permissions": res_perm,
        }

        thing_picture(
            con=self.con,
            label="ThingPicture",
            bitstream=resource_bitstream,
            permissions=res_perm,
            values={"anything:hasPictureTitle": make_value(value="A Thing Picture named Lena", permissions=res_perm)},
        ).create()


if __name__ == "__main__":
    pytest.main([__file__])
