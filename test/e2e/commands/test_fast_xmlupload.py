import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.commands.fast_xmlupload.process_files import process_files
from dsp_tools.commands.fast_xmlupload.upload_files import upload_files
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.xmlupload_ingest.upload_xml import fast_xmlupload


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
    txt_files = ["processed_files.txt", "unprocessed_files.txt"]

    @classmethod
    def setUpClass(cls) -> None:
        """
        Is executed once before the methods of this class are run
        """
        create_project(
            project_file_as_path_or_parsed=cls.json_file,
            server=cls.dsp_url,
            user_mail=cls.user,
            password=cls.password,
            verbose=False,
            dump=False,
        )
        Path(cls.input_dir / "nested").mkdir()
        Path(cls.input_dir / "nested/subfolder").mkdir()
        shutil.copy(cls.input_dir / "test.jpg", cls.input_dir / "nested/test.jpg")
        shutil.copy(cls.input_dir / "test.jpg", cls.input_dir / "nested/subfolder/test.jpg")

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Remove the testdata/bitstreams/nested folder and the testdata/preprocessed_files folder.
        Is executed after the methods of this class have all run through.
        """
        shutil.rmtree(cls.input_dir / "nested")
        shutil.rmtree(cls.output_dir)

    def tearDown(self) -> None:
        """
        Delete all pickle files, all id2iri files and all "(un)processed_files.txt" files.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        for pickle_file in list(Path().glob("*.pkl")):
            pickle_file.unlink()

        for id2iri_file in list(Path().glob("*id2iri_mapping*.json")):
            id2iri_file.unlink()

        for txt_file in self.txt_files:
            Path(txt_file).unlink(missing_ok=True)

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

        pickle_files = list(Path().glob("*.pkl"))
        self.assertEqual(len(pickle_files), 1)

        print("test_fast_xmlupload: call upload_files()")
        success_upload = upload_files(
            dir_with_processed_files=self.output_dir,
            nthreads=4,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url,
        )
        self.assertTrue(success_upload)

        print("test_fast_xmlupload: call xmlupload_ingest()")
        success_fast_xmlupload = fast_xmlupload(
            xml_file=self.xml_file,
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url,
        )
        self.assertTrue(success_fast_xmlupload)


if __name__ == "__main__":
    pytest.main([__file__])
