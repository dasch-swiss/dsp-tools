# pylint: disable=duplicate-code,missing-class-docstring

import os
import unittest

import pytest

from dsp_tools.excel2xml import _derandomize_xsd_id
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.xml_upload import xml_upload


class TestImportScripts(unittest.TestCase):

    def tearDown(self) -> None:
        """
        Remove generated data. This method is executed after every test method.
        """
        if os.path.isfile("src/dsp_tools/import_scripts/data-processed.xml"):
            os.remove("src/dsp_tools/import_scripts/data-processed.xml")


    @pytest.mark.filterwarnings("ignore")
    def test_import_scripts(self) -> None:
        """
        Execute the import script in its directory, create the project on the DSP server, and upload the created XML to
        the DSP server.
        """
        # pull the latest state of the git submodule
        os.system("git submodule update --init --recursive")
        from dsp_tools.import_scripts import \
            import_script  # pylint: disable=import-outside-toplevel

        # execute the import script in its directory
        old_working_directory = os.getcwd()
        os.chdir("src/dsp_tools/import_scripts")
        try:
            import_script.main()
        finally:
            os.chdir(old_working_directory)

        # check the output XML (but before, remove random components from resource IDs and resptr targets)
        with open("testdata/excel2xml/00A1-data-processed-expected.xml", encoding="utf-8") as f:
            xml_expected = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        with open("src/dsp_tools/import_scripts/data-processed.xml", encoding="utf-8") as f:
            xml_returned = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        self.assertEqual(xml_expected, xml_returned)

        # create the JSON project file, and upload the XML
        success_on_creation = create_project(
            project_file_as_path_or_parsed="src/dsp_tools/import_scripts/import_project.json",
            server="http://0.0.0.0:3333",
            user_mail="root@example.com",
            password="test",
            verbose=False,
            dump=False
        )
        self.assertTrue(success_on_creation)

        success_on_xmlupload = xml_upload(
            input_file="src/dsp_tools/import_scripts/data-processed.xml",
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            imgdir="src/dsp_tools/import_scripts/",
            sipi="http://0.0.0.0:1024",
            verbose=False,
            incremental=False,
            save_metrics=False,
            preprocessing_done=False
        )
        self.assertTrue(success_on_xmlupload)


if __name__ == "__main__":
    pytest.main([__file__])
