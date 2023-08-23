import unittest

import pytest
from lxml import etree

from dsp_tools.models.xmlvalue import XMLValue


class TestXmlValue(unittest.TestCase):
    def test_unformatted_text_value(self) -> None:
        unformatted_text_orig = """

                Poem
                with 1 line break:
                and 2 line breaks:

                and 3 line breaks:


                and     multiple     spaces	and		tabstops ...
                
                and spaces on empty lines.


            """
        unformatted_text_expected = (
            "Poem"
            "\n"
            "with 1 line break:\n"
            "and 2 line breaks:\n\n"
            "and 3 line breaks:\n\n"  # max. 1 empty line. 2+ are replaced by 1.
            "and multiple spaces and tabstops ...\n\n"
            "and spaces on empty lines."
        )
        unformatted_node = etree.fromstring(
            f'<unformatted-text-prop name=":foo"><text>{unformatted_text_orig}</text></unformatted-text-prop>'
        )
        unformatted_xml_value = XMLValue(unformatted_node, "unformatted-text")
        self.assertEqual(unformatted_xml_value.value, unformatted_text_expected)


if __name__ == "__main__":
    pytest.main([__file__])
