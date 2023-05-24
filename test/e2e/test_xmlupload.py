# pylint: disable=missing-class-docstring,missing-function-docstring

import logging
import unittest

import pytest

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.xml_upload import xml_upload

logger = logging.getLogger(__name__)

class TestXMLUpload(unittest.TestCase):

    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    imgdir = "."
    sipi = "http://0.0.0.0:1024"

    def test_xml_upload(self) -> None:
        with self.assertRaisesRegex(
            UserError, 
            r"A project with shortcode 9999 could not be found on the DSP server"
        ):
            xml_upload(
                input_file="testdata/invalid-testdata/xml-data/inexistent-shortcode.xml",
                server=self.server,
                user=self.user,
                password=self.password,
                imgdir=self.imgdir,
                sipi=self.sipi,
                verbose=True,
                incremental=False,
                save_metrics=False,
                preprocessing_done=False,
                logger_instance=logger
            )
        
        with self.assertRaisesRegex(
            UserError, 
            r"The <knora> tag of your XML file references the ontology 'notexistingfantasyonto', "
            r"but the project 4124 on the DSP server doesn't contain an ontology with this name"
        ):
            xml_upload(
                input_file="testdata/invalid-testdata/xml-data/inexistent-ontoname.xml",
                server=self.server,
                user=self.user,
                password=self.password,
                imgdir=self.imgdir,
                sipi=self.sipi,
                verbose=True,
                incremental=False,
                save_metrics=False,
                preprocessing_done=False,
                logger_instance=logger
            )

if __name__ == "__main__":
    pytest.main([__file__])
