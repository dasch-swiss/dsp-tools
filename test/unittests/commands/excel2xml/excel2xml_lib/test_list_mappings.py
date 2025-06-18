import unittest

from dsp_tools.commands import excel2xml

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestListMappings(unittest.TestCase):
    def test_create_json_excel_list_mapping(self) -> None:
        # We start with an Excel column that contains list nodes, but with spelling errors
        excel_column = [
            "  first noude ov testlist  ",
            "sekond noude ov testlist",
            " fierst sobnode , sekond sobnode , Third Node Ov Testliest",  # multiple entries per cell are possible
            "completely wrong spelling variant of 'first subnode' that needs manual correction",
        ]
        corrections = {
            "completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode"
        }
        testlist_mapping_returned = excel2xml.create_json_excel_list_mapping(
            path_to_json="testdata/json-project/test-project-systematic.json",
            list_name="testlist",
            excel_values=excel_column,
            sep=",",
            corrections=corrections,
        )
        testlist_mapping_expected = {
            "first noude ov testlist": "first node of testlist",
            "sekond noude ov testlist": "second node of testlist",
            "fierst sobnode": "first subnode",
            "sekond sobnode": "second subnode",
            "Third Node Ov Testliest": "third node of testlist",
            "third node ov testliest": "third node of testlist",
            "completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode",
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)

    def test_create_json_list_mapping(self) -> None:
        testlist_mapping_returned = excel2xml.create_json_list_mapping(
            path_to_json="testdata/json-project/test-project-systematic.json",
            list_name="testlist",
            language_label="en",
        )
        testlist_mapping_expected = {
            "First node of the Test-List": "first node of testlist",
            "first node of the test-list": "first node of testlist",
            "First Sub-Node": "first subnode",
            "first sub-node": "first subnode",
            "Second Sub-Node": "second subnode",
            "second sub-node": "second subnode",
            "Second node of the Test-List": "second node of testlist",
            "second node of the test-list": "second node of testlist",
            "Third node of the Test-List": "third node of testlist",
            "third node of the test-list": "third node of testlist",
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)
