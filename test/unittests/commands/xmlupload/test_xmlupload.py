import unittest

import pytest

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.models.exceptions import BaseError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestConvertArkToResourceIRI(unittest.TestCase):
    def test_good(self) -> None:
        ark = "ark:/72163/080c-779b9990a0c3f-6e"
        iri = convert_ark_v0_to_resource_iri(ark)
        self.assertEqual("http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q", iri)

    def test_invalid_ark(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'\. The ARK seems to be invalid"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")

    def test_invalid_shortcode(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'\. Invalid project shortcode '080X'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")

    def test_invalid_shortcode_long(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'\. Invalid project shortcode '080C1'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")

    def test_invalid_salsah_id(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b99\+90a0c3f-6e'\. Invalid Salsah ID '779b99\+90a0c3f'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")


if __name__ == "__main__":
    pytest.main([__file__])
