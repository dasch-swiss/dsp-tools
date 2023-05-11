import os
import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.fast_xmlupload.process_files import process_files
from dsp_tools.fast_xmlupload.upload_files import upload_files
from dsp_tools.fast_xmlupload.upload_xml import fast_xmlupload
from dsp_tools.utils.project_create import create_project


class TestFastXmlUpload(unittest.TestCase):
    """
    Test the fast XML upload
    """

    dsp_url = "http://0.0.0.0:3333"
    sipi_url = "http://0.0.0.0:1024"
    user = "root@example.com"
    password = "test"

    xml_file = "xml-data/test-data-fast-xmlupload.xml"
    dir_with_processed_files = "preprocessed_files"
    original_cwd = ""
    pickle_file = Path()


    def setUp(self) -> None:
        """
        Is executed before any test is run.
        """
        self.original_cwd = os.getcwd()
        os.chdir("testdata")
        create_project(
            project_file_as_path_or_parsed="json-project/test-project-fast-xmlupload.json",
            server=self.dsp_url,
            user_mail=self.user,
            password=self.password,
            verbose=False,
            dump=False
        )
        shutil.copytree("bitstreams", "bitstreams/nested")
        shutil.copytree("bitstreams/nested", "bitstreams/nested/subfolder")


    def tearDown(self) -> None:
        """
        Is executed after all tests have run through.
        """
        shutil.rmtree("bitstreams/nested")
        shutil.rmtree(self.dir_with_processed_files)
        self.pickle_file.unlink()
        id2iri_search_results = list(Path().glob("*id2iri_mapping.json"))
        if len(id2iri_search_results) == 1:
            id2iri_search_results[0].unlink()
        os.chdir(self.original_cwd)


    def test_fast_xmlupload(self) -> None:
        """
        Test if it is possible to call the 3 steps of the fast XML upload, one after the other.
        No detailed tests are done here, it is only tested if the 3 steps can be called.
        """
        print("test_fast_xmlupload: call process_files()")
        success_process = process_files(
            input_dir="bitstreams",
            output_dir=self.dir_with_processed_files,
            xml_file=self.xml_file,
            nthreads=None
        )
        self.assertTrue(success_process)

        self.pickle_file = list(Path().glob("*.pkl"))[0]
        
        print(f"test_fast_xmlupload: call upload_files() with pickle file {self.pickle_file}")
        success_upload = upload_files(
            pkl_file=str(self.pickle_file),
            dir_with_processed_files=self.dir_with_processed_files,
            nthreads=None,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url
        )
        self.assertTrue(success_upload)

        print("test_fast_xmlupload: call fast_xmlupload()")
        success_fast_xmlupload = fast_xmlupload(
            xml_file=self.xml_file,
            pkl_file=str(self.pickle_file),
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url
        )
        self.assertTrue(success_fast_xmlupload)


if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
        