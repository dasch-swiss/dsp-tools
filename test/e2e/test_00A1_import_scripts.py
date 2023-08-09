# pylint: disable=missing-class-docstring,duplicate-code

import os
import re
import subprocess
import unittest

import pytest

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.shared import check_notna
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
        subprocess.run("git submodule update --init --recursive", check=True, shell=True)
        from dsp_tools.import_scripts import import_script  # pylint: disable=import-outside-toplevel

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
            dump=False,
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
            preprocessing_done=False,
        )
        self.assertTrue(success_on_xmlupload)


def _derandomize_xsd_id(
    string: str,
    multiple_occurrences: bool = False,
) -> str:
    """
    In some contexts, the random component of the output of make_xsd_id_compatible() is a hindrance,
    especially for testing.
    This method removes the random part,
    but leaves the other modifications introduced by make_xsd_id_compatible() in place.
    This method's behaviour is defined by the example in the "Examples" section.

    Args:
        string: the output of make_xsd_id_compatible()
        multiple_occurrences: If true, string can be an entire XML document, and all occurrences will be removed

    Raises:
        BaseError: if the input cannot be derandomized

    Returns:
        the derandomized string

    Examples:
        >>> id_1 = make_xsd_id_compatible("Hello!")
        >>> id_2 = make_xsd_id_compatible("Hello!")
        >>> assert _derandomize_xsd_id(id_1) == _derandomize_xsd_id(id_2)
    """
    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be derandomized.")

    uuid4_regex = r"[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
    if multiple_occurrences:
        return re.subn(uuid4_regex, "", string, flags=re.IGNORECASE)[0]
    else:
        return re.sub(uuid4_regex, "", string, re.IGNORECASE)


if __name__ == "__main__":
    pytest.main([__file__])
