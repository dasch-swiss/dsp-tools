from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

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
from dsp_tools.xmllib.value_checkers import is_nonempty_value
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
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
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

    @staticmethod
    def new(
        res_id: str,
        restype: str,
        label: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> Resource:
        """
        Creates a new resource

        Args:
            res_id: Resource ID
            restype: Resource type
            label: Resource label
            permissions: permission of the resource, default is `PROJECT_SPECIFIC_PERMISSIONS`

        Warnings:
            - If res_id is not non-empty
            - If restype is not non-empty
            - If label is not non-empty

        Returns:
            Resource
        """
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
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
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
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a boolean value to the resource

        Accepted values: "false", "0", "0.0", "no", "true", "1", "1.0", "yes"
        Wrong values:    anything else
        Conversions:     "false", "0", "0.0", "no" -> "false"
                         "true", "1", "1.0", "yes" -> "true"

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_bool_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a boolean value to the resource if it is non-empty

        Accepted values: "false", "0", "0.0", "no", "true", "1", "1.0", "yes"
        Wrong values:    anything else
        Conversions:     "false", "0", "0.0", "no" -> "false"
                         "true", "1", "1.0", "yes" -> "true"

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(BooleanValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # ColorValue
    #######################

    def add_color(
        self,
        prop_name: str,
        value: int | str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a color value to the resource

        Accepted values: `#[0-9a-f]{6}`
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_color_multiple(
        self,
        prop_name: str,
        values: list[int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several color values to the resource

        Accepted values: list of `#[0-9a-f]{6}`
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([ColorValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_color_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a color value to the resource if it is non-empty

        Accepted values: `#[0-9a-f]{6}`
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # DateValue
    #######################

    def add_date(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a date value to the resource

        Accepted values: Date in the format according to the documentation
        Wrong values:    any other format
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_date_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several date values to the resource

        Accepted values: list of dates in the format according to the documentation
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([DateValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_date_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a date value to the resource if it is non-empty

        Accepted values: Date in the format according to the documentation
        Wrong values:    any other format
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # DecimalValue
    #######################

    def add_decimal(
        self,
        prop_name: str,
        value: float | str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a decimal value to the resource

        Accepted values: decimals, integers in numeric forms or scientific notation (eg: 1e2)
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_decimal_multiple(
        self,
        prop_name: str,
        values: list[float | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several decimal values to the resource

        Accepted values: list of decimals, integers in numeric forms or scientific notation (eg: 1e2)
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([DecimalValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_decimal_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a decimal value to the resource if it is non-empty

        Accepted values: decimals, integers in numeric forms or scientific notation (eg: 1e2)
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # GeonameValue
    #######################

    def add_geoname(
        self,
        prop_name: str,
        value: int | str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a geoname value to the resource

        Accepted values: string of integers
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_geoname_multiple(
        self,
        prop_name: str,
        values: list[int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several geoname values to the resource

        Accepted values: list integer strings
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([GeonameValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_geoname_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a geoname value to the resource if it is non-empty

        Accepted values: string of integers
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # IntValue
    #######################

    def add_integer(
        self,
        prop_name: str,
        value: int | str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a integer value to the resource

        Accepted values: integer
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_integer_multiple(
        self,
        prop_name: str,
        values: list[int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several integer values to the resource

        Accepted values: list of integers
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([IntValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_integer_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a integer value to the resource if it is non-empty

        Accepted values: integer
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # LinkValue
    #######################

    def add_link(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a link value to the resource

        Accepted values: ID of another resource
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_link_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several link values to the resource

        Accepted values: list of resource IDs
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([LinkValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_link_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a link value to the resource if it is non-empty

        Accepted values: ID of another resource
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # ListValue
    #######################

    def add_list(
        self,
        prop_name: str,
        list_name: Any,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a list value to the resource

        Accepted values: non-empty value
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            list_name: name of the list
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    def add_list_multiple(
        self,
        prop_name: str,
        list_name: Any,
        values: list[Any],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several list values to the resource

        Accepted values: list of non-empty values
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            list_name: name of the list
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([ListValue(v, list_name, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_list_optional(
        self,
        prop_name: str,
        list_name: Any,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a list value to the resource if it is non-empty

        Accepted values: non-empty value
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            list_name: name of the list
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TextValue: SimpleText
    #######################

    def add_simpletext(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a simple text value to the resource

        Accepted values: simple text string
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_simpletext_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several simple text values to the resource

        Accepted values: list of simple text strings
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([SimpleText(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_simpletext_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a simple text value to the resource if it is non-empty

        Accepted values: simple text string
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TextValue: Richtext
    #######################

    def add_richtext(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        """
        Adds a rich text value to the resource

        Accepted values: richtext as a string
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None
            newline_replacement: Options to replace the `\\n` with XML tags, default `<br/>`

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        value = replace_newlines_with_tags(str(value), newline_replacement)
        self.values.append(Richtext(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_richtext_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        """
        Adds several rich text values to the resource

        Accepted values: list of richtexts as a string
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None
            newline_replacement: Options to replace the `\\n` with XML tags, default `<br/>`

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        values = [replace_newlines_with_tags(str(v), newline_replacement) for v in values]
        self.values.extend([Richtext(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_richtext_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        """
        Adds a rich text value to the resource if it is non-empty

        Accepted values: richtext as a string
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None
            newline_replacement: Options to replace the `\\n` with XML tags, default `<br/>`

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            value = replace_newlines_with_tags(str(value), newline_replacement)
            self.values.append(Richtext(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # TimeValue
    #######################

    def add_time(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a time value to the resource

        Accepted values: valid timestamp
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(TimeValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_time_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several time values to the resource

        Accepted values: list of timestamps
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([TimeValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_time_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a time value to the resource if it is non-empty

        Accepted values: valid timestamp
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(TimeValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # UriValue
    #######################

    def add_uri(
        self,
        prop_name: str,
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a URI value to the resource

        Accepted values: valid URI
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.append(UriValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_uri_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds several URI values to the resource

        Accepted values: list of URIs
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            values: values to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            Resource
        """
        self.values.extend([UriValue(v, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_uri_optional(
        self,
        prop_name: str,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Adds a URI value to the resource if it is non-empty

        Accepted values: valid URI
        Wrong values:    anything else
        Conversions:     None

        Args:
            prop_name: name of the property
            value: value to add
            permissions: value permissions, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            Resource
        """
        if is_nonempty_value(value):
            self.values.append(UriValue(value, prop_name, permissions, comment, self.res_id))
        return self

    #######################
    # AbstractFileValue
    #######################

    def add_file(
        self,
        filename: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a file (bitstream) to the resource

        Args:
            filename: path to the file
            permissions: permissions of the file, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the filename is not string like

        Raises:
            If a file or IIIF URI value already exists

        Returns:
            Resource
        """
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name '{filename}' cannot be added."
            )
        self.file_value = FileValue(filename, permissions, comment, self.res_id)
        return self

    def add_iiif_uri(
        self,
        iiif_uri: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a IIIF URI to the resource

        Args:
            iiif_uri: valid IIIF URI
            permissions: permissions of the value, default is `PROJECT_SPECIFIC_PERMISSIONS`
            comment: optional comment, default is None

        Warnings:
            If the IIIF URI is not according to the official specifications

        Raises:
            If a file or IIIF URI value already exists

        Returns:
            Resource
        """
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
        """
        Add metadata from a SALSAH migration

        Args:
            creation_date: Creation date of the resource
            iri: Original IRI
            ark: Original ARK

        Raises:
            InputError: if metadata already exists

        Returns:
            Resource
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self
