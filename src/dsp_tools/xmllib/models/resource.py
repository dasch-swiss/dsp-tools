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
        Create a new resource.

        Args:
            res_id: Resource ID
            restype: Resource type
            label: Resource label
            permissions: optional permissions of this resource

        Warnings:
            - If res_id is empty
            - If restype is empty
            - If label is empty

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
        value: bool | str | int | float,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a boolean value to the resource.
        Boolean values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean.

        Accepted values: "false", "0", "0.0", "no", "true", "1", "1.0", "yes".

        Conversions:
         - "false", "0", "0.0", "no" -> "false"
         - "true", "1", "1.0", "yes" -> "true"

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Boolean values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean.

        Accepted values: "false", "0", "0.0", "no", "true", "1", "1.0", "yes".

        Conversions:
         - "false", "0", "0.0", "no" -> "false"
         - "true", "1", "1.0", "yes" -> "true"

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        value: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a color value to the resource.
        Color values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color.

        Args:
            prop_name: name of the property
            value: color value as `#` followed by 6 hexadecimal digits
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
        """
        self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_color_multiple(
        self,
        prop_name: str,
        values: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several color values to the resource.
        Color values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color.

        Args:
            prop_name: name of the property
            values: color values as `#` followed by 6 hexadecimal digits
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Color values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color.

        Args:
            prop_name: name of the property
            value: color value as `#` followed by 6 hexadecimal digits
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a date value to the resource.
        Date values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several date values to the resource.
        Date values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date.

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Date values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        value: float | int | str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a decimal value to the resource.
        Decimal values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal.

        Args:
            prop_name: name of the property
            value: value to add (if provided as string, it must be convertible to int/float)
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
        """
        self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_decimal_multiple(
        self,
        prop_name: str,
        values: list[float | int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several decimal values to the resource.
        Decimal values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal.

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Decimal values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a [geonames.org](geonames.org) value to the resource.
        The [geonames.org](geonames.org) identifier must be provided as integer 
        or string that is convertible to integer.
        Geoname values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname.

        Args:
            prop_name: name of the property
            value: [geonames.org](geonames.org) identifier to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several [geonames.org](geonames.org) values to the resource.
        The [geonames.org](geonames.org) identifiers must be provided as integers
        or strings that are convertible to integers.
        Geoname values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname.

        Args:
            prop_name: name of the property
            values: [geonames.org](geonames.org) identifiers to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        The [geonames.org](geonames.org) identifier must be provided as integer 
        or string that is convertible to integer.
        Geoname values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname.

        Args:
            prop_name: name of the property
            value: [geonames.org](geonames.org) identifier to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add an integer value to the resource.
        Integer values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer.

        Args:
            prop_name: name of the property
            value: value to add. If it is provided as string, it must be convertible to integer.
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several integer values to the resource.
        Integer values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer.

        Args:
            prop_name: name of the property
            values: values to add. If they are provided as strings, they must be convertible to integers.
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Integer values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer.

        Args:
            prop_name: name of the property
            value: value to add. If it is provided as string, it must be convertible to integer.
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a link value to the resource, in the form of an ID of another resource.
        Link values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr.

        Args:
            prop_name: name of the property
            value: ID of the target resource
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several link values to the resource, in the form of IDs of other resources.
        Link values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr.

        Args:
            prop_name: name of the property
            values: IDs of the target resources
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        If non-empty, the value must be an ID of another resource.
        Link values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr.

        Args:
            prop_name: name of the property
            value: ID of target resource
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        list_name: str | int | float,
        value: str | int | float,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a list value to the resource, i.e. a name of a list node.
        List values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list.

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            value: name of a list node (N.B. not the label, but the name of the list node)
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
        """
        self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    def add_list_multiple(
        self,
        prop_name: str,
        list_name: str | int | float,
        values: list[str | int | float],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several list values to the resource, i.e. names of list nodes.
        List values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list.

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            values: names of list nodes (N.B. not the labels, but the names of the list nodes)
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
        """
        self.values.extend([ListValue(v, list_name, prop_name, permissions, comment, self.res_id) for v in values])
        return self

    def add_list_optional(
        self,
        prop_name: str,
        list_name: str | int | float,
        value: Any,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        List values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list.

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            value: name of a list node (N.B. not the label, but the name of the list node)
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a simple text value to the resource.
        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            value: text value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several simple text values to the resource.
        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            values: text values to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            value: text value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a rich text value to the resource.
        Rich text values must be provided as strings, potentially containing DSP Standard Standoff Markup XML tags
        as documented in https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/.
        Only the documented tags are allowed.

        By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
        Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.

        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            value: rich text value as string, potentially containing DSP Standard Standoff Markup XML tags
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: Options how to deal with `\\n` inside the text value. Default: replace with `<br/>`.

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several rich text values to the resource.
        Rich text values must be provided as strings, potentially containing DSP Standard Standoff Markup XML tags
        as documented in https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/.
        Only the documented tags are allowed.

        By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
        Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.

        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            values: rich text values as strings, potentially containing DSP Standard Standoff Markup XML tags
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: Options how to deal with `\\n` inside the text value. Default: replace with `<br/>`.

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Rich text values must be provided as strings, potentially containing DSP Standard Standoff Markup XML tags
        as documented in https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/.
        Only the documented tags are allowed.

        By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
        Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.

        Text values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text.

        Args:
            prop_name: name of the property
            value: rich text value as string, potentially containing DSP Standard Standoff Markup XML tags
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: Options how to deal with `\\n` inside the text value. Default: replace with `<br/>`.

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a time value to the resource.
        Time values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several time values to the resource.
        Time values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time.

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        Time values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a URI value to the resource.
        URI values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add several URI values to the resource.
        URI values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri.

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the values are not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added values
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
        If the value is not empty, add it to the resource, otherwise return the resource unchanged.
        URI values are documented at https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri.

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the value is not amongst the accepted formats.

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a file (bitstream) to the resource.

        Args:
            filename: path to the file
            permissions: optional permissions of this file
            comment: optional comment

        Warnings:
            If the filename is not string like

        Raises:
            InputError: If the resource already has a file or IIIF URI value

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add a IIIF URI to the resource.

        Args:
            iiif_uri: valid IIIF URI
            permissions: optional permissions of this value
            comment: optional comment

        Warnings:
            If the IIIF URI is not according to the official specifications

        Raises:
            InputError: If the resource already has a file or IIIF URI value

        Returns:
            The original resource that this method has been called on, with the added value
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
        Add metadata from a SALSAH migration.

        Args:
            creation_date: Creation date of the resource in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original resource that this method has been called on, with the added migration metadata
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self
