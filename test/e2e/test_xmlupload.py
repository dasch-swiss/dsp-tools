# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest

import pytest

from dsp_tools.command.xmlupload import xmlupload
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.xmlupload.upload_config import UploadConfig


class TestXMLUpload(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    imgdir = "."
    sipi = "http://0.0.0.0:1024"

    def test_xml_upload(self) -> None:
        with self.assertRaisesRegex(UserError, r"A project with shortcode 9999 could not be found on the DSP server"):
            xmlupload(
                input_file="testdata/invalid-testdata/xml-data/inexistent-shortcode.xml",
                server=self.server,
                user=self.user,
                password=self.password,
                imgdir=self.imgdir,
                sipi=self.sipi,
                config=UploadConfig(),
            )

        with self.assertRaisesRegex(
            UserError,
            r"The <knora> tag of your XML file references the default-ontology 'notexistingfantasyonto', "
            r"but the project 4124 on the DSP server contains only the ontologies {'testonto'}",
        ):
            xmlupload(
                input_file="testdata/invalid-testdata/xml-data/inexistent-ontoname.xml",
                server=self.server,
                user=self.user,
                password=self.password,
                imgdir=self.imgdir,
                sipi=self.sipi,
                config=UploadConfig(),
            )


if __name__ == "__main__":
    pytest.main([__file__])
