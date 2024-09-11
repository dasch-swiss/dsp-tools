from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.commands.xmllib import BooleanValue
from dsp_tools.commands.xmllib import ColorValue
from dsp_tools.commands.xmllib import DateValue
from dsp_tools.commands.xmllib import DecimalValue
from dsp_tools.commands.xmllib import GeonameValue
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
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_bools(
        self, values: list[Any], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([BooleanValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_bool_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # ColorValue
    ###################

    def add_color(
        self, value: int | str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_colors(
        self, values: list[int | str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([ColorValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_color_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            ColorValue(value, prop_name, permissions, comment, self.res_id)
        return self

    ###################
    # DateValue
    ###################

    def add_date(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_dates(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([DateValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_date_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # DecimalValue
    ###################

    def add_decimal(
        self, value: float | str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_decimals(
        self, values: list[float | str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([DecimalValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_decimal_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # GeonameValue
    ###################

    def add_geoname(
        self, value: int | str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_geonames(
        self, values: list[int | str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_geoname_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    ###################
    # IntValue
    ###################

    def add_integer(
        self, value: int | str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_integers(
        self, values: list[int | str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([IntValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_integer_optional(
        self, value: Any, prop_name: Any, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # LinkValue
    ###################

    def add_link(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_links(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([LinkValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_link_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # ListValue
    ###################

    def add_list(
        self, value: Any, listname: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_lists(
        self,
        values: list[Any],
        listname: Any,
        prop_name: str,
        permissions: str | None = None,
        comment: str | None = None,
    ) -> Resource:
        pass

    def add_list_optional(
        self, value: Any, listname: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    ###################
    # TextValue: SimpleText
    ###################

    def add_simple_text(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_simple_texts(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        self.values.extend([SimpleText(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_simple_text_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    ###################
    # TextValue: Richtext
    ###################

    def add_richtext(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_richtexts(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_richtext_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    ###################
    # TimeValue
    ###################

    def add_time(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_times(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_time_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    ###################
    # UriValue
    ###################

    def add_uri(
        self, value: str, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_uris(
        self, values: list[str], prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    def add_uri_optional(
        self, value: Any, prop_name: str, permissions: str | None = None, comment: str | None = None
    ) -> Resource:
        pass

    ###################
    # AbstractFileValue
    ###################

    def add_file(self, filename: str, permissions: str | None = None, comment: str | None = None) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name: '{filename}' cannot be added."
            )
        self.file_value = FileValue(filename, permissions, comment, self.res_id)
        return self

    def add_iiif_uri(self, iiif_uri: str, permissions: str | None = None, comment: str | None = None) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name: '{iiif_uri}' cannot be added."
            )
        self.file_value = IIIFUri(iiif_uri, permissions, comment, self.res_id)
        return self
