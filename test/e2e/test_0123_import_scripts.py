import filecmp
import glob
import os
import re
import unittest
from zipfile import ZipFile

import pytest

from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.xml_upload import xml_upload


class TestImportScripts(unittest.TestCase):

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
        self.assertListEqual(original_files, original_files_expected, "docs/assets/0123-import-scripts.zip is outdated")

        # check that the files have the same size and modification time
        for orig, extr in zip(original_files, extracted_files):
            self.assertTrue(filecmp.cmp(orig, extr), "docs/assets/0123-import-scripts.zip is outdated")

    @pytest.mark.filterwarnings("ignore")
    def test_import_scripts(self) -> None:
        """
        Execute the import script in its directory, create the project on the DSP server, and upload the created XML to
        the DSP server.
        """
        # execute the import script in its directory, and check if the output XML is as expected
        old_working_directory = os.getcwd()
        os.chdir("docs/assets/0123-import-scripts")
        with open("import-script.py") as f:
            import_script = f.read()
            exec(import_script, {})
        with open("../../../testdata/data-processed-expected.xml") as f:
            data_processed_expected = f.read()
            # remove the resource ids, because they contain a random component
            data_processed_expected = re.sub(r'(?<!permissions )id=".+?"', "", data_processed_expected)
        with open("data-processed.xml") as f:
            data_processed_returned = f.read()
            # remove the resource ids, because they contain a random component
            data_processed_returned = re.sub(r'(?<!permissions )id=".+?"', "", data_processed_returned)

        self.assertEqual(data_processed_expected, data_processed_returned)

        # create the JSON project file, and upload the XML
        success_on_creation = create_project(
            input_file="import-project.json",
            server="http://0.0.0.0:3333",
            user_mail="root@example.com",
            password="test",
            verbose=False,
            dump=False
        )
        self.assertTrue(success_on_creation)

        success_on_xmlupload = xml_upload(
            input_file="data-processed.xml",
            server="http://0.0.0.0:3333",
            user="root@example.com",
            password="test",
            imgdir=".",
            sipi="http://0.0.0.0:1024",
            verbose=False,
            incremental=False
        )
        self.assertTrue(success_on_xmlupload)

        # delete generated data, restore working directory
        if os.path.isfile("data-processed.xml"):
            os.remove("data-processed.xml")
        os.chdir(old_working_directory)


if __name__ == '__main__':
    unittest.main()
