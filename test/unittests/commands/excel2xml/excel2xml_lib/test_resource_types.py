import unittest
from typing import Callable

import regex
from lxml import etree

from dsp_tools.commands import excel2xml
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestResourceTypes(unittest.TestCase):
    def test_make_annotation(self) -> None:
        expected = '<annotation label="label" id="id" permissions="open"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_permission(self) -> None:
        expected = '<annotation label="label" id="id" permissions="restricted"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", "restricted"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_ark(self) -> None:
        expected = '<annotation label="label" id="id" permissions="open" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_iri(self) -> None:
        expected = '<annotation label="label" id="id" permissions="open" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_creation_date(self) -> None:
        expected = '<annotation label="label" id="id" permissions="open" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_annotation_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_annotation("label", "id", ark="ark", iri="iri")

    def test_fail_annotation_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_annotation("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_link(self) -> None:
        expected = '<link label="label" id="id" permissions="open"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id"))
        self.assertEqual(expected, result)

    def test_make_link_with_permission(self) -> None:
        expected = '<link label="label" id="id" permissions="restricted"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", "restricted"))
        self.assertEqual(expected, result)

    def test_make_link_with_ark(self) -> None:
        expected = '<link label="label" id="id" permissions="open" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_link_with_iri(self) -> None:
        expected = '<link label="label" id="id" permissions="open" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_link_with_creation_date(self) -> None:
        expected = '<link label="label" id="id" permissions="open" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_link_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_link("label", "id", ark="ark", iri="iri")

    def test_fail_link_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_link("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_region(self) -> None:
        expected = '<region label="label" id="id" permissions="open"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id"))
        self.assertEqual(expected, result)

    def test_make_region_with_permission(self) -> None:
        expected = '<region label="label" id="id" permissions="restricted"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", "restricted"))
        self.assertEqual(expected, result)

    def test_make_region_with_ark(self) -> None:
        expected = '<region label="label" id="id" permissions="open" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_region_with_iri(self) -> None:
        expected = '<region label="label" id="id" permissions="open" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_region_with_creation_date(self) -> None:
        expected = '<region label="label" id="id" permissions="open" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_region_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_region("label", "id", ark="ark", iri="iri")

    def test_fail_region_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_region("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_audio_segment(self) -> None:
        expected = '<audio-segment label="label" id="id" permissions="open"/>'
        result = _strip_namespace(excel2xml.make_audio_segment("label", "id"))
        self.assertEqual(expected, result)

    def test_make_audio_segment_with_custom_permissions(self) -> None:
        expected = '<audio-segment label="label" id="id" permissions="restricted"/>'
        result = _strip_namespace(excel2xml.make_audio_segment("label", "id", "restricted"))
        self.assertEqual(expected, result)

    def test_make_video_segment(self) -> None:
        expected = '<video-segment label="label" id="id" permissions="open"/>'
        result = _strip_namespace(excel2xml.make_video_segment("label", "id"))
        self.assertEqual(expected, result)

    def test_make_video_segment_with_custom_permissions(self) -> None:
        expected = '<video-segment label="label" id="id" permissions="restricted"/>'
        result = _strip_namespace(excel2xml.make_video_segment("label", "id", "restricted"))
        self.assertEqual(expected, result)

    def test_make_resource(self) -> None:
        test_cases: list[tuple[Callable[..., etree._Element], str]] = [
            (
                lambda: excel2xml.make_resource("label", "restype", "id"),
                '<resource label="label" restype="restype" id="id" permissions="open"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", "restricted"),
                '<resource label="label" restype="restype" id="id" permissions="restricted"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", ark="ark"),
                '<resource label="label" restype="restype" id="id" permissions="open" ark="ark"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", iri="iri"),
                '<resource label="label" restype="restype" id="id" permissions="open" iri="iri"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12Z"),
                (
                    '<resource label="label" restype="restype" id="id" permissions="open" '
                    'creation_date="2019-10-23T13:45:12Z"/>'
                ),
            ),
        ]

        for method, result in test_cases:
            xml_returned_as_element = method()
            xml_returned = etree.tostring(xml_returned_as_element, encoding="unicode")
            xml_returned = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned)
            self.assertEqual(result, xml_returned)

        self.assertWarns(
            DspToolsUserWarning, lambda: excel2xml.make_resource("label", "restype", "id", ark="ark", iri="iri")
        )
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12")


def _strip_namespace(element: etree._Element) -> str:
    """Removes the namespace from the XML element."""
    xml = etree.tostring(element, encoding="unicode")
    xml = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", xml)
    return xml
