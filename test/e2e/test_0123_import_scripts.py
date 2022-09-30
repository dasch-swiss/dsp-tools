import os
import re
import unittest

import git
import pytest

from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.xml_upload import xml_upload


class TestImportScripts(unittest.TestCase):

    @pytest.mark.filterwarnings("ignore")
    def test_import_scripts(self) -> None:
        # a ZIP of the directory docs/assets/0123-import-scripts is available for download on docs.dasch.swiss. To
        # make sure that the ZIP is not older than any file in the directory, it must be checked that the UNIX time
        # stamp of the last commit of the ZIP is >= the UNIX time stamp of the last commit of any file in the directory
        # See https://git-scm.com/docs/pretty-formats#Documentation/pretty-formats.txt-emadem
        # and https://git-scm.com/docs/git-log#Documentation/git-log.txt---ltpathgt82308203
        repo = git.Git(".")
        zip_last_commit_date = repo.log("--pretty=format:%at", "docs/assets/0123-import-scripts.zip").split("\n")[0]
        dir_last_commit_date = repo.log("--pretty=format:%at", "docs/assets/0123-import-scripts").split("\n")[0]
        self.assertGreaterEqual(zip_last_commit_date, dir_last_commit_date)

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
