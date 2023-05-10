import os
import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.fast_xmlupload.process_files import process_files
from dsp_tools.fast_xmlupload.upload_files import upload_files
from dsp_tools.fast_xmlupload.upload_xml import fast_xml_upload
from dsp_tools.utils.project_create import create_project


class TestTools(unittest.TestCase):

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
        is executed before all tests
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
        is executed after all tests are run through
        """
        shutil.rmtree("bitstreams/nested")
        shutil.rmtree(self.dir_with_processed_files)
        self.pickle_file.unlink()
        list(Path().glob("*id2iri_mapping.json"))[0].unlink()
        os.chdir(self.original_cwd)


    def test_fast_xml_upload(self) -> None:
        print("test_fast_xml_upload: call process_files()")
        success_process = process_files(
            input_dir="bitstreams",
            output_dir=self.dir_with_processed_files,
            xml_file=self.xml_file,
            nthreads=None
        )
        self.assertTrue(success_process)

        self.pickle_file = list(Path().glob("*.pkl"))[0]
        
        print(f"test_fast_xml_upload: call upload_files() with pickle file {self.pickle_file}")
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

        print("test_fast_xml_upload: call fast_xml_upload()")
        success_fast_xml_upload = fast_xml_upload(
            xml_file=self.xml_file,
            pkl_file=str(self.pickle_file),
            user=self.user,
            password=self.password,
            dsp_url=self.dsp_url,
            sipi_url=self.sipi_url
        )
        self.assertTrue(success_fast_xml_upload)


if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
        # extensions: dict[str, list[str]] = dict()
        # extensions[":ImageThing"] = [".jpg", ".jpeg", ".tif", ".tiff", ".jp2", ".png"]
        # extensions[":MovieThing"] = [".mp4"]
        # extensions[":ZipThing"] = [".7z", ".gz", ".gzip", ".tar", ".tar.gz", ".tgz", ".z", ".zip"]
        # extensions[":TextThing"] = [".csv", ".txt", ".xml", ".xsd", ".xsl"]
        # extensions[":DocumentThing"] = [".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"]
        # extensions[":AudioThing"] = [".mp3", ".wav"]
        
        # # generate an XML file that uses these files
        # root = excel2xml.make_root(shortcode="00E0", default_ontology="testonto")
        # root = excel2xml.append_permissions(root)
        # for filepath in Path("testdata/bitstreams").glob("*.*"):
        #     resource = excel2xml.make_resource(
        #         label=str(filepath),
        #         restype=[rt for rt, ext in extensions.items() if filepath.suffix in ext][0],
        #         id=excel2xml.make_xsd_id_compatible(str(filepath))
        #     )
        #     warnings.filterwarnings("ignore")
        #     resource.append(excel2xml.make_bitstream_prop(filepath))
        #     root.append(resource)
        # excel2xml.write_xml(root, str(testproject / "data.xml"))
        
