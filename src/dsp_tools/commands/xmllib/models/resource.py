from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.commands.xmllib.models.file_values import AbstractFileValue
from dsp_tools.commands.xmllib.models.file_values import FileValue
from dsp_tools.commands.xmllib.models.file_values import IIIFUri
from dsp_tools.commands.xmllib.models.values import IntValue
from dsp_tools.commands.xmllib.models.values import LinkValue
from dsp_tools.commands.xmllib.models.values import SimpleText
from dsp_tools.commands.xmllib.models.values import Value
from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError

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
    # BooleanValue
    ###################

    def add_bool(
        self, prop_name: str, value: Any, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_bools(
        self, prop_name: str, values: list[Any], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_bool_optional(
        self, prop_name: str, value: Any, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # ColorValue
    ###################

    def add_color(
        self, prop_name: str, value: int, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_colors(
        self, prop_name: str, values: list[int], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_color_optional(
        self, prop_name: str, value: int, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # DateValue
    ###################

    def add_date(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_dates(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_date_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # DecimalValue
    ###################

    def add_decimal(
        self, prop_name: str, value: float, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_decimals(
        self, prop_name: str, values: list[float], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_decimal_optional(
        self, prop_name: str, value: float, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # GeonameValue
    ###################

    def add_geoname(
        self, prop_name: str, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_geonames(
        self, prop_name: str, values: list[int | str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_geoname_optional(
        self, prop_name: str, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # IntValue
    ###################

    def add_integer(
        self, prop_name: str, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_integers(
        self, prop_name: str, values: list[int | str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.values.append(IntValue(value=v, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_integer_optional(
        self, prop_name: Any, value: int | str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    ###################
    # LinkValue
    ###################

    def add_link(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(LinkValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_links(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.values.append(LinkValue(value=v, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_link_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(LinkValue(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    ###################
    # ListValue
    ###################

    def add_list(
        self, prop_name: str, value: Any, listname: Any, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_lists(
        self,
        prop_name: str,
        values: list[Any],
        listname: Any,
        permissions: str | None = None,
        comments: str | None = None,
    ) -> Resource:
        pass

    def add_list_optional(
        self, prop_name: str, value: Any, listname: Any, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # TextValue: SimpleText
    ###################

    def add_simple_text(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        self.values.append(SimpleText(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_simple_texts(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        for v in values:
            self.values.append(SimpleText(value=v, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    def add_simple_text_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(SimpleText(value=value, prop_name=prop_name, permissions=permissions, comment=comments))
        return self

    ###################
    # TextValue: Richtext
    ###################

    def add_richtext(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_richtexts(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_richtext_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # TimeValue
    ###################

    def add_time(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_times(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_time_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    ###################
    # UriValue
    ###################

    def add_uri(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_uris(
        self, prop_name: str, values: list[str], permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

    def add_uri_optional(
        self, prop_name: str, value: str, permissions: str | None = None, comments: str | None = None
    ) -> Resource:
        pass

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
        self.file_value = IIIFUri(value=iiif_uri, permissions=permissions, comment=comments)
        return self
