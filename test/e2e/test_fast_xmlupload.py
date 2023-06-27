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

    input_dir = Path("testdata/bitstreams")
    output_dir = "testdata/preprocessed_files"
    xml_file = "testdata/xml-data/test-data-fast-xmlupload.xml"
    json_file = "testdata/json-project/test-project-fast-xmlupload.json"

    @classmethod
    def setUpClass(cls) -> None:
        """
        Is executed before the methods of this class are run
        """
        create_project(
            project_file_as_path_or_parsed=cls.json_file,
            server=cls.dsp_url,
            user_mail=cls.user,
            password=cls.password,
            verbose=False,
            dump=False,
        )
        shutil.copytree(cls.input_dir, cls.input_dir / "nested")
        shutil.copytree(cls.input_dir / "nested", cls.input_dir / "nested/subfolder")

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Is executed after the methods of this class have all run through
        """
        shutil.rmtree(cls.input_dir / "nested")
        shutil.rmtree(cls.output_dir)

    def tearDown(self) -> None:
        """
        Is executed after each test method
        """
        for pickle_file in list(Path().glob("*.pkl")):
            pickle_file.unlink()
        
        id2iri_search_results = list(Path().glob("*id2iri_mapping.json"))
        if len(id2iri_search_results) == 1:
            id2iri_search_results[0].unlink()
        
        Path("processed_files.txt").unlink(missing_ok=True)
        Path("unprocessed_files.txt").unlink(missing_ok=True)
        

    def test_fast_xmlupload(self) -> None:
        """
        Test if it is possible to call the 3 steps of the fast XML upload, one after the other.
        No detailed tests are done here, it is only tested if the 3 steps can be called.
        """
        print("test_fast_xmlupload: call process_files()")
        success_process = process_files(
            input_dir=str(self.input_dir),
            output_dir=self.output_dir,
            xml_file=self.xml_file,
            nthreads=None,
        )
        self.assertTrue(success_process)

        pickle_file = str(list(Path().glob("*.pkl"))[0])

        print(f"test_fast_xmlupload: call upload_files() with pickle file {pickle_file}")
        success_upload = upload_files(
            pkl_file=pickle_file,
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
            pkl_file=pickle_file,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url,
        )
        self.assertTrue(success_fast_xmlupload)

    def test_batch_size_of_process_files(self) -> None:
        """
        Test if the "batch_size" parameter of process_files() function works.
        """
        exit_codes = []
        for _ in range(3):
            with self.assertRaises(SystemExit) as cm:
                process_files(
                    input_dir=str(self.input_dir),
                    output_dir=self.output_dir,
                    xml_file=self.xml_file,
                    nthreads=None,
                    batch_size=40,
                )
            exit_codes.append(cm.exception.code)
        self.assertEqual(exit_codes, [2, 2, 0])


if __name__ == "__main__":
    pytest.main([__file__])
