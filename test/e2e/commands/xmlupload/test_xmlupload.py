# pylint: disable=missing-class-docstring
# ruff: noqa: D102 (undocumented-public-method)

import unittest

import pytest

from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import BaseError


class TestXMLUpload(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    imgdir = "."
    sipi = "http://0.0.0.0:1024"

    def test_error_on_nonexistant_shortcode(self) -> None:
        with self.assertRaisesRegex(BaseError, r"A project with shortcode 9999 could not be found on the DSP server"):
            xmlupload(
                input_file="testdata/invalid-testdata/xml-data/inexistent-shortcode.xml",
                server=self.server,
                user=self.user,
                password=self.password,
                imgdir=self.imgdir,
                sipi=self.sipi,
                config=UploadConfig(),
            )

    def test_error_on_nonexistant_onto_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"The default ontology 'notexistingfantasyonto' "):
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
