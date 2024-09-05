from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any
from typing import Protocol

from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.uri_util import is_iiif_uri

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


class AbstractFileValue(Protocol):
    value: str | Path
    permissions: str | None
    comment: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError


class FileValue(AbstractFileValue):
    value: str | Path
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __init__(
        self, filename: str, permissions: str | None = None, comments: str | None = None, res_id: str | None = None
    ) -> None:
        self.value = filename
        self.permissions = permissions
        self.comment = comments

        if not is_string(self.value):
            _warn_type_mismatch(expected_type="file name", value=self.value, res_id=res_id)

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}bitstream", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


class IIIFUri(AbstractFileValue):
    value: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __init__(
        self, iiif_uri: str, permissions: str | None = None, comments: str | None = None, res_id: str | None = None
    ) -> None:
        self.value = iiif_uri
        self.permissions = permissions
        self.comment = comments

        if not is_iiif_uri(self.value):
            _warn_type_mismatch(expected_type="IIIF-URI", value=self.value, res_id=res_id)

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}iiif-uri", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


def _warn_type_mismatch(expected_type: str, value: Any, res_id: str) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"The Resource '{res_id}' has an invalid {expected_type}. The expected value is {value}."
    warnings.warn(DspToolsUserWarning(msg))
