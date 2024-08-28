from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.commands.xmllib.models.values import AbstractFileValue
from dsp_tools.commands.xmllib.models.values import FileValue
from dsp_tools.commands.xmllib.models.values import IIIFUri
from dsp_tools.commands.xmllib.models.values import IntValue
from dsp_tools.commands.xmllib.models.values import LinkValue
from dsp_tools.commands.xmllib.models.values import SimpleText
from dsp_tools.commands.xmllib.models.values import Value
from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.uri_util import is_iiif_uri

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class Resource:
    res_id: str
    restype: str
    label: str
    values: list[Value] = field(default_factory=list)
    permissions: str = "res-default"
    file_value: AbstractFileValue | None = None

    def __post_init__(self) -> None:
        if not is_string(str(self.label)):
            msg = (
                f"The label of a resource should be a string.\n"
                f"The label '{self.label}' of the resource with the ID {self.res_id} is not a string."
            )
            warnings.warn(DspToolsUserWarning(msg))

    def serialise(self) -> etree._Element:
        res_ele = self._make_resource_ele()
        if self.file_value:
            res_ele.append(self.file_value.serialise())
        res_ele.extend(self._serialise_values())
        return res_ele

    def _make_resource_ele(self) -> etree._Element:
        attribs = {"label": self.label, "restype": self.restype, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{DASCH_SCHEMA}resource", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_values(self) -> list[etree._Element]:
        grouped = defaultdict(list)
        for val in self.values:
            grouped[val.prop_name].append(val)
        return [self._combine_values(prop_values) for prop_values in grouped.values()]

    @staticmethod
    def _combine_values(prop_values: list[Value]) -> etree._Element:
        prop_ = prop_values[0].make_prop()
        prop_eles = [x.make_element() for x in prop_values]
        prop_.extend(prop_eles)
        return prop_

    ###################
    # IntValues
    ###################

    def add_integer(
        self, prop_name: str, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not is_integer(value):
            _warn_type_mismatch(expected_type="integer", res_id=self.res_id, value=value, prop_name=prop_name)
        self.values.append(IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_integers(
        self, prop_name: str, values: list[int | str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.add_integer(prop_name=prop_name, value=v, permissions=permissions, comments=comments)
        return self

    def add_integer_optional(
        self, prop_name: Any, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    ###################
    # TextValue: SimpleText
    ###################

    def add_simple_text(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not is_string(value):
            _warn_type_mismatch(expected_type="string", res_id=self.res_id, value=value, prop_name=prop_name)
        self.values.append(SimpleText(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_simple_texts(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.add_simple_text(prop_name=prop_name, value=v, permissions=permissions, comments=comments)
        return self

    def add_simple_text_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.add_simple_text(prop_name=prop_name, value=value, permissions=permissions, comments=comments)
        return self

    ###################
    # LinkValue
    ###################

    def add_link(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not is_string(value):
            _warn_type_mismatch(expected_type="string", res_id=self.res_id, value=value, prop_name=prop_name)
        self.values.append(LinkValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_links(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.add_link(prop_name=prop_name, value=v, permissions=permissions, comments=comments)
        return self

    def add_link_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.add_link(prop_name=prop_name, value=value, permissions=permissions, comments=comments)
        return self

    ###################
    # AbstractFileValue
    ###################

    def add_file(self, filename: str, permissions: str | None = None, comments: str | None = None) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name: '{filename}' cannot be added."
            )
        self.file_value = FileValue(value=filename, permissions=permissions, comment=comments)
        return self

    def add_iiif_uri(self, iiif_uri: str, permissions: str | None = None, comments: str | None = None) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name: '{iiif_uri}' cannot be added."
            )
        if not is_iiif_uri(iiif_uri):
            _warn_type_mismatch(expected_type="IIIF-URI", res_id=self.res_id, value=iiif_uri)
        self.file_value = IIIFUri(value=iiif_uri, permissions=permissions, comment=comments)
        return self


def _warn_type_mismatch(expected_type: str, res_id: str, value: Any, prop_name: str | None = None) -> None:
    locs = f"    Resource ID: {res_id} | Value: {value}"
    if prop_name:
        locs += f" | Property: {prop_name}"
    msg = f"The following value is not a valid {expected_type}.\n{locs}"
    warnings.warn(DspToolsUserWarning(msg))
