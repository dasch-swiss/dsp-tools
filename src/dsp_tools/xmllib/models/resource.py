from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.models.file_values import AbstractFileValue
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.models.migration_metadata import MigrationMetadata
from dsp_tools.xmllib.models.user_enums import NewlineReplacement
from dsp_tools.xmllib.models.user_enums import Permissions
from dsp_tools.xmllib.models.values import BooleanValue
from dsp_tools.xmllib.models.values import ColorValue
from dsp_tools.xmllib.models.values import DateValue
from dsp_tools.xmllib.models.values import DecimalValue
from dsp_tools.xmllib.models.values import GeonameValue
from dsp_tools.xmllib.models.values import IntValue
from dsp_tools.xmllib.models.values import LinkValue
from dsp_tools.xmllib.models.values import ListValue
from dsp_tools.xmllib.models.values import Richtext
from dsp_tools.xmllib.models.values import SimpleText
from dsp_tools.xmllib.models.values import TimeValue
from dsp_tools.xmllib.models.values import UriValue
from dsp_tools.xmllib.models.values import Value
from dsp_tools.xmllib.value_checkers import is_string_like
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

LIST_SEPARATOR = "\n    - "


@dataclass
class Resource:
    res_id: str
    restype: str
    label: str
    values: list[Value] = field(default_factory=list)
    permissions: Permissions = Permissions.DOAP
    file_value: AbstractFileValue | None = None
    migration_metadata: MigrationMetadata | None = None

    def __post_init__(self) -> None:
        msg = []
        if not is_string_like(str(self.label)):
            msg.append(f"Label '{self.label}'")
        if not is_string_like(str(self.res_id)):
            msg.append(f"Resource ID '{self.res_id}'")
        if not is_string_like(str(self.restype)):
            msg.append(f"Resource Type '{self.restype}'")
        if msg:
            out_msg = (
                f"The Resource with the ID '{self.res_id}' should have strings in the following field(s), "
                f"the input is not a valid string.:{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg)}"
            )
            warnings.warn(DspToolsUserWarning(out_msg))

    def new(self, res_id: str, restype: str, label: str, permissions: Permissions = Permissions.DOAP) -> Resource:
        return Resource(
            res_id=res_id,
            restype=restype,
            label=label,
            permissions=permissions,
        )

    def serialise(self) -> etree._Element:
        res_ele = self._serialise_resource_element()
        if self.file_value:
            res_ele.append(self.file_value.serialise())
        res_ele.extend(self._serialise_values())
        return res_ele

    def _serialise_resource_element(self) -> etree._Element:
        attribs = {"label": self.label, "restype": self.restype, "id": self.res_id}
        if self.permissions != Permissions.DOAP:
            attribs["permissions"] = self.permissions.value
        return etree.Element(f"{DASCH_SCHEMA}resource", attrib=attribs, nsmap=XML_NAMESPACE_MAP)

    def _serialise_values(self) -> list[etree._Element]:
        grouped = defaultdict(list)
        for val in self.values:
            grouped[val.prop_name].append(val)
        return [self._combine_values(prop_values) for prop_values in grouped.values()]

    def _combine_values(self, prop_values: list[Value]) -> etree._Element:
        prop_ = prop_values[0].make_prop()
        prop_eles = [x.make_element() for x in prop_values]
        prop_.extend(prop_eles)
        return prop_

    #######################
    # BooleanValue
    #######################

    def add_bool(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_bools(
        self,
        values: list[Any],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([BooleanValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_bool_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # ColorValue
    #######################

    def add_color(
        self,
        value: int | str,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_colors(
        self,
        values: list[int | str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([ColorValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_color_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # DateValue
    #######################

    def add_date(
        self, value: str, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_dates(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([DateValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_date_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # DecimalValue
    #######################

    def add_decimal(
        self,
        value: float | str,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_decimals(
        self,
        values: list[float | str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([DecimalValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_decimal_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # GeonameValue
    #######################

    def add_geoname(
        self,
        value: int | str,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_geonames(
        self,
        values: list[int | str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([GeonameValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_geoname_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # IntValue
    #######################

    def add_integer(
        self,
        value: int | str,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_integers(
        self,
        values: list[int | str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([IntValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_integer_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # LinkValue
    #######################

    def add_link(
        self, value: str, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_links(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([LinkValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_link_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # ListValue
    #######################

    def add_list(
        self,
        value: Any,
        list_name: Any,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    def add_lists(
        self,
        values: list[Any],
        list_name: Any,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([ListValue(v, list_name, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_list_optional(
        self,
        value: Any,
        list_name: Any,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TextValue: SimpleText
    #######################

    def add_simpletext(
        self, value: str, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_simpletexts(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([SimpleText(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_simpletext_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TextValue: Richtext
    #######################

    def add_richtext(
        self,
        value: str,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        value = replace_newlines_with_tags(str(value), newline_replacement)
        self.values.append(Richtext(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_richtexts(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        values = [replace_newlines_with_tags(str(v), newline_replacement) for v in values]
        self.values.extend([Richtext(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_richtext_optional(
        self,
        value: Any,
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        if not pd.isna(value):
            value = replace_newlines_with_tags(str(value), newline_replacement)
            self.values.append(Richtext(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TimeValue
    #######################

    def add_time(
        self, value: str, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(TimeValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_times(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([TimeValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_time_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(TimeValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # UriValue
    #######################

    def add_uri(
        self, value: str, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        self.values.append(UriValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_uris(
        self,
        values: list[str],
        prop_name: str,
        permissions: Permissions = Permissions.DOAP,
        comment: str | None = None,
    ) -> Resource:
        self.values.extend([UriValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_uri_optional(
        self, value: Any, prop_name: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if not pd.isna(value):
            self.values.append(UriValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # AbstractFileValue
    #######################

    def add_file(
        self, filename: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name '{filename}' cannot be added."
            )
        self.file_value = FileValue(filename, permissions, comment, self.res_id)
        return self

    def add_iiif_uri(
        self, iiif_uri: str, permissions: Permissions = Permissions.DOAP, comment: str | None = None
    ) -> Resource:
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name '{iiif_uri}' cannot be added."
            )
        self.file_value = IIIFUri(iiif_uri, permissions, comment, self.res_id)
        return self

    #######################
    # Migration Metadata
    #######################

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> Resource:
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self
