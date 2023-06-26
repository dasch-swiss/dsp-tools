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

    input_dir = "testdata/bitstreams"
    output_dir = "testdata/preprocessed_files"
    xml_file = "testdata/xml-data/test-data-fast-xmlupload.xml"
    json_file = "testdata/json-project/test-project-fast-xmlupload.json"
    pickle_file = ""

    def setUp(self) -> None:
        """
        Is executed before any test is run.
        """
        create_project(
            project_file_as_path_or_parsed=self.json_file,
            server=self.dsp_url,
            user_mail=self.user,
            password=self.password,
            verbose=False,
            dump=False,
        )
        shutil.copytree("testdata/bitstreams", "testdata/bitstreams/nested")
        shutil.copytree("testdata/bitstreams/nested", "testdata/bitstreams/nested/subfolder")

    def tearDown(self) -> None:
        """
        Is executed after all tests have run through.
        """
        shutil.rmtree("testdata/bitstreams/nested")
        shutil.rmtree(self.output_dir)
        if Path(self.pickle_file).is_file():
            Path(self.pickle_file).unlink()
        id2iri_search_results = list(Path().glob("*id2iri_mapping.json"))
        if len(id2iri_search_results) == 1:
            id2iri_search_results[0].unlink()

    def test_fast_xmlupload(self) -> None:
        """
        Test if it is possible to call the 3 steps of the fast XML upload, one after the other.
        No detailed tests are done here, it is only tested if the 3 steps can be called.
        """
        print("test_fast_xmlupload: call process_files()")
        success_process = process_files(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            xml_file=self.xml_file,
            nthreads=None,
        )
        self.assertTrue(success_process)

        self.pickle_file = str(list(Path().glob("*.pkl"))[0])

        print(f"test_fast_xmlupload: call upload_files() with pickle file {self.pickle_file}")
        success_upload = upload_files(
            pkl_file=self.pickle_file,
            dir_with_processed_files=self.output_dir,
            nthreads=4,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url,
        )
        self.assertTrue(success_upload)

        print("test_fast_xmlupload: call fast_xmlupload()")
        success_fast_xmlupload = fast_xmlupload(
            xml_file=self.xml_file,
            pkl_file=self.pickle_file,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url,
        )
        self.assertTrue(success_fast_xmlupload)


if __name__ == "__main__":
    pytest.main([__file__])
