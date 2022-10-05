import os
import unittest

import pytest

from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.xml_upload import xml_upload
from knora.excel2xml import _derandomize_xsd_id


class TestImportScripts(unittest.TestCase):

    def tearDown(self) -> None:
        """
        Remove generated data. This method is executed after every test method.
        """
        if os.path.isfile("knora/dsplib/import_scripts/data-processed.xml"):
            os.remove("knora/dsplib/import_scripts/data-processed.xml")


    @pytest.mark.filterwarnings("ignore")
    def test_import_scripts(self) -> None:
        """
        Execute the import script in its directory, create the project on the DSP server, and upload the created XML to
        the DSP server.
        """
        # pull the latest state of the git submodule


        # execute the import script in its directory
        old_working_directory = os.getcwd()
        os.chdir("knora/dsplib/import_scripts")
        try:
            os.system("git pull")
            from knora.dsplib.import_scripts import import_script
            import_script.main()
        finally:
            os.chdir(old_working_directory)

        # check the output XML (but before, remove random components from resource IDs and resptr targets)
        with open("testdata/0123-data-processed-expected.xml") as f:
            xml_expected = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        with open("knora/dsplib/import_scripts/data-processed.xml") as f:
            xml_returned = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        self.assertEqual(xml_expected, xml_returned)

        # create the JSON project file, and upload the XML
        success_on_creation = create_project(
            input_file="knora/dsplib/import_scripts/import_project.json",
            server="http://0.0.0.0:3333",
            user_mail="root@example.com",
            password="test",
            verbose=False,
            dump=False
        )
        self.assertTrue(success_on_creation)

        success_on_xmlupload = xml_upload(
            input_file="knora/dsplib/import_scripts/data-processed.xml",
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            imgdir="knora/dsplib/import_scripts/",
            sipi="http://0.0.0.0:1024",
            verbose=False,
            incremental=False
        )
        self.assertTrue(success_on_xmlupload)


if __name__ == '__main__':
    unittest.main()
