import filecmp
import glob
import os
import re
import shutil
import unittest
from zipfile import ZipFile

import pytest

from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.xml_upload import xml_upload
from knora.excel2xml import _derandomize_xsd_id


class TestImportScripts(unittest.TestCase):

    def tearDown(self) -> None:
        """
        Remove generated data. This method is executed after every test method.
        """
        shutil.rmtree("docs/assets/0123-import-scripts-extracted", ignore_errors=True)
        if os.path.isfile("docs/assets/0123-import-scripts/data-processed.xml"):
            os.remove("docs/assets/0123-import-scripts/data-processed.xml")


    def test_zip_folder(self) -> None:
        """
        A ZIP of the directory docs/assets/0123-import-scripts is available for download on docs.dasch.swiss. Make
        sure that the ZIP's contents are identical to the directory
        """
        with ZipFile("docs/assets/0123-import-scripts.zip", "r") as zipfolder:
            zipfolder.extractall("docs/assets/0123-import-scripts-extracted")
        original_files = [x for x in glob.glob("docs/assets/0123-import-scripts/**", recursive=True) if os.path.isfile(x)]
        extracted_files = [x for x in glob.glob("docs/assets/0123-import-scripts-extracted/0123-import-scripts/**", recursive=True)
                           if os.path.isfile(x)]

        # check that for every original file, there is exactly one extracted counterpart
        original_files_expected = [re.sub(r"0123-import-scripts-extracted/", "", x) for x in extracted_files]
        self.assertListEqual(sorted(original_files), sorted(original_files_expected), "docs/assets/0123-import-scripts.zip is outdated")

        # check that the files have the same size and modification time
        for orig, extr in zip(sorted(original_files), sorted(extracted_files)):
            self.assertTrue(filecmp.cmp(orig, extr), "docs/assets/0123-import-scripts.zip is outdated")


    @pytest.mark.filterwarnings("ignore")
    def test_import_scripts(self) -> None:
        """
        Execute the import script in its directory, create the project on the DSP server, and upload the created XML to
        the DSP server.
        """
        # execute the import script in its directory
        old_working_directory = os.getcwd()
        os.chdir("docs/assets/0123-import-scripts")
        try:
            with open("import-script.py") as f:
                import_script = f.read()
                exec(import_script, {})
        finally:
            os.chdir(old_working_directory)

        # check if the output XML is as expected (first, remove all random components in the resource IDs and resptr targets
        with open("testdata/0123-data-processed-expected.xml") as f:
            xml_expected = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        with open("docs/assets/0123-import-scripts/data-processed.xml") as f:
            xml_returned = _derandomize_xsd_id(f.read(), multiple_occurrences=True)
        self.assertEqual(xml_expected, xml_returned)

        # create the JSON project file, and upload the XML
        success_on_creation = create_project(
            input_file="docs/assets/0123-import-scripts/import-project.json",
            server="http://0.0.0.0:3333",
            user_mail="root@example.com",
            password="test",
            verbose=False,
            dump=False
        )
        self.assertTrue(success_on_creation)

        success_on_xmlupload = xml_upload(
            input_file="docs/assets/0123-import-scripts/data-processed.xml",
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            imgdir=".",
            sipi="http://0.0.0.0:1024",
            verbose=False,
            incremental=False
        )
        self.assertTrue(success_on_xmlupload)


if __name__ == '__main__':
    unittest.main()
