from __future__ import annotations

import warnings
from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.internal_helpers import check_and_create_richtext_string
from dsp_tools.xmllib.internal_helpers import check_and_fix_collection_input
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.config_options import PreDefinedLicense
from dsp_tools.xmllib.models.file_values import AbstractFileValue
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.models.file_values import Metadata
from dsp_tools.xmllib.models.migration_metadata import MigrationMetadata
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

# ruff: noqa: D101, D102

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
    def create_new(
        res_id: str,
        restype: str,
        label: str,
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    ) -> Resource:
        """
        Create a new resource.

        Args:
            res_id: resource ID
            restype: resource type
            label: resource label
            permissions: optional permissions of this resource

        Returns:
            Resource

        Examples:
            ```python
            resource = xmllib.Resource.create_new(
                res_id="ID",
                restype=":ResourceType",
                label="label",
            )
            ```

            ```python
            # resource with restricted permissions
            resource = xmllib.Resource.create_new(
                res_id="ID",
                restype=":ResourceType",
                label="label",
                permissions=xmllib.Permissions.RESTRICTED,
            )
            ```
        """
        return Resource(
            res_id=res_id,
            restype=restype,
            label=label,
            permissions=permissions,
        )

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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean)

        Conversions:
         - The conversion is case-insensitive, meaning that the words can also be capitalised.
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `false`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja` -> `true`

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_bool(
                prop_name=":propName",
                value=True
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean)

        Conversions:
         - The conversion is case-insensitive, meaning that the words can also be capitalised.
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `false`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja` -> `true`

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_bool_optional(
                prop_name=":propName",
                value=True
            )
            ```

            ```python
            resource = resource.add_bool_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_color(
                prop_name=":propName",
                value="#00ff66",
            )
            ```
        """
        self.values.append(ColorValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_color_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several color values to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_color_multiple(
                prop_name=":propName",
                values=["#00ff66", "#00ff55"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([ColorValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_color_optional(
                prop_name=":propName",
                value="#00ff66",
            )
            ```

            ```python
            resource = resource.add_color_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_date(
                prop_name=":propName",
                value="GREGORIAN:CE:2014-01-31:CE:2014-01-31",
            )
            ```
        """
        self.values.append(DateValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_date_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several date values to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_date_multiple(
                prop_name=":propName",
                values=["GREGORIAN:CE:2014-01-31:CE:2014-01-31", "CE:1849:CE:1850"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([DateValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_date_optional(
                prop_name=":propName",
                value="CE:1849:CE:1850",
            )
            ```

            ```python
            resource = resource.add_date_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        If the value is provided as string, it must be convertible to integer or float.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_decimal(
                prop_name=":propName",
                value=1.4,
            )
            ```
        """
        self.values.append(DecimalValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_decimal_multiple(
        self,
        prop_name: str,
        values: Collection[float | int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several decimal values to the resource.
        If the values are provided as string, they must be convertible to integer or float.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_decimal_multiple(
                prop_name=":propName",
                values=[1.4, 2.9],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([DecimalValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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
        If the value is provided as string, it must be convertible to integer or float.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_decimal_optional(
                prop_name=":propName",
                value=1.0,
            )
            ```

            ```python
            resource = resource.add_decimal_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        Add a [geonames.org](https://www.geonames.org/) value to the resource.
        The [geonames.org](https://www.geonames.org/) identifier must be provided as integer
        or string that is convertible to integer.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname)


        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_geoname(
                prop_name=":propName",
                value="2761369",
            )
            ```
        """
        self.values.append(GeonameValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_geoname_multiple(
        self,
        prop_name: str,
        values: Collection[int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several [geonames.org](https://www.geonames.org/) values to the resource.
        The [geonames.org](https://www.geonames.org/) identifiers must be provided as integers
        or strings that are convertible to integers.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_geoname_multiple(
                prop_name=":propName",
                values=["2761369", "2661604"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([GeonameValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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
        The [geonames.org](https://www.geonames.org/) identifier must be provided as integer
        or string that is convertible to integer.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_geoname_optional(
                prop_name=":propName",
                value="2661604",
            )
            ```

            ```python
            resource = resource.add_geoname_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        If the value is provided as string, it must be convertible to integer.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_integer(
                prop_name=":propName",
                value=399,
            )
            ```
        """
        self.values.append(IntValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_integer_multiple(
        self,
        prop_name: str,
        values: Collection[int | str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several integer values to the resource.
        If the values are provided as string, they must be convertible to integer.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_integer_multiple(
                prop_name=":propName",
                values=[24, "66"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([IntValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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
        If the value is provided as string, it must be convertible to integer.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_integer_optional(
                prop_name=":propName",
                value="2604",
            )
            ```

            ```python
            resource = resource.add_integer_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr)

        Args:
            prop_name: name of the property
            value: target resource ID
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_link(
                prop_name=":propName",
                value="target_resource_id",
            )
            ```
        """
        self.values.append(LinkValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_link_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several link values to the resource, in the form of IDs of other resources.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr)

        Args:
            prop_name: name of the property
            values: list of target resources IDs
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_link_multiple(
                prop_name=":propName",
                values=["target_resource_id_1", "target_resource_id_2"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([LinkValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr)

        Args:
            prop_name: name of the property
            value: target resource ID or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_link_optional(
                prop_name=":propName",
                value="target_resource_id",
            )
            ```

            ```python
            resource = resource.add_link_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list)

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            value: name of a list node (N.B. not the label, but the name of the list node)
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_list(
                prop_name=":propName",
                list_name="listName",
                value="nodeName",
            )
            ```
        """
        self.values.append(ListValue(value, list_name, prop_name, permissions, comment, self.res_id))
        return self

    def add_list_multiple(
        self,
        prop_name: str,
        list_name: str | int | float,
        values: Collection[str | int | float],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several list values to the resource, i.e. names of list nodes.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list)

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            values: names of list nodes (N.B. not the labels, but the names of the list nodes)
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_list_multiple(
                prop_name=":propName",
                list_name="listName",
                values=["nodeName_1", "nodeName_2"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([ListValue(v, list_name, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list)

        Args:
            prop_name: name of the property
            list_name: name of the list (N.B. not the label, but the name of the list)
            value: name of a list node (N.B. not the label, but the name of the list node) or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_list_optional(
                prop_name=":propName",
                list_name="listName",
                value="nodeName",
            )
            ```

            ```python
            resource = resource.add_list_optional(
                prop_name=":propName",
                list_name="listName",
                value=None,
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_simpletext(
                prop_name=":propName",
                value="text",
            )
            ```
        """
        self.values.append(SimpleText(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_simpletext_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several simple text values to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_simpletext_multiple(
                prop_name=":propName",
                values=["text 1", "text 2"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([SimpleText(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_simpletext_optional(
                prop_name=":propName",
                value="text",
            )
            ```

            ```python
            resource = resource.add_simpletext_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        as [documented here.](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/)
        Only the documented tags are allowed.

        Conversions:
            By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
            Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.
            [Click here for more details](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/value-converters/#xmllib.value_converters.replace_newlines_with_tags)

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_richtext(
                prop_name=":propName",
                value="line 1\\nline 2",
            )
            ```

            ```python
            # changing the replacement options for newlines `\\n`
            resource = resource.add_richtext(
                prop_name=":propName",
                value="line 1\\nline 2",
                newline_replacement=xmllib.NewlineReplacement.PARAGRAPH,
            )
            ```
        """
        checked_text = check_and_create_richtext_string(
            value=value,
            prop_name=prop_name,
            newline_replacement=newline_replacement,
            res_id=self.res_id,
        )
        self.values.append(
            Richtext(
                value=checked_text,
                prop_name=prop_name,
                permissions=permissions,
                comment=comment,
                resource_id=self.res_id,
            )
        )
        return self

    def add_richtext_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
        newline_replacement: NewlineReplacement = NewlineReplacement.LINEBREAK,
    ) -> Resource:
        """
        Add several rich text values to the resource.
        Rich text values must be provided as strings, potentially containing DSP Standard Standoff Markup XML tags
        as [documented here.](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/)
        Only the documented tags are allowed.

        Conversions:
            By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
            Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.
            [Click here for more details](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/value-converters/#xmllib.value_converters.replace_newlines_with_tags)

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_richtext_multiple(
                prop_name=":propName",
                values=["<strong>Bold text</strong>", "text 2"],
            )
            ```
        """
        checked_text = [
            check_and_create_richtext_string(
                value=v,
                prop_name=prop_name,
                newline_replacement=newline_replacement,
                res_id=self.res_id,
            )
            for v in values
        ]
        self.values.extend(
            [
                Richtext(
                    value=v,
                    prop_name=prop_name,
                    permissions=permissions,
                    comment=comment,
                    resource_id=self.res_id,
                )
                for v in checked_text
            ]
        )
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
        as [documented here.](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/)
        Only the documented tags are allowed.

        Conversions:
            By default, replace newline characters inside the text value with `<br/>`, which preserves the linebreak.
            Without this replacement, the newline would disappear, because `\\n` is meaningless in an XML file.
            [Click here for more details](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/value-converters/#xmllib.value_converters.replace_newlines_with_tags)

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment
            newline_replacement: options how to deal with `\\n` inside the text value. Default: replace with `<br/>`

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_richtext_optional(
                prop_name=":propName",
                value="<strong>Bold text</strong>",
            )
            ```

            ```python
            resource = resource.add_richtext_optional(
                prop_name=":propName",
                value=None,
            )
            ```
        """
        if is_nonempty_value(value):
            return self.add_richtext(prop_name, value, permissions, comment, newline_replacement)
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_time(
                prop_name=":propName",
                value="2019-10-23T13:45:12Z",
            )
            ```
        """
        self.values.append(TimeValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_time_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several time values to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_time_multiple(
                prop_name=":propName",
                values=["2019-10-23T13:45:12Z", "2009-10-10T12:00:00-05:00"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([TimeValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_time_optional(
                prop_name=":propName",
                value="2019-10-23T13:45:12Z",
            )
            ```

            ```python
            resource = resource.add_time_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri)

        Args:
            prop_name: name of the property
            value: value to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_uri(
                prop_name=":propName",
                value="https://dasch.swiss",
            )
            ```
        """
        self.values.append(UriValue(value, prop_name, permissions, comment, self.res_id))
        return self

    def add_uri_multiple(
        self,
        prop_name: str,
        values: Collection[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add several URI values to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri)

        Args:
            prop_name: name of the property
            values: values to add
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added values

        Examples:
            ```python
            resource = resource.add_uri_multiple(
                prop_name=":propName",
                values=["https://dasch.swiss", "https://docs.dasch.swiss"],
            )
            ```
        """
        vals = check_and_fix_collection_input(values, prop_name, self.res_id)
        self.values.extend([UriValue(v, prop_name, permissions, comment, self.res_id) for v in vals])
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

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri)

        Args:
            prop_name: name of the property
            value: value to add or empty value
            permissions: optional permissions of this value
            comment: optional comment

        Returns:
            The original resource, with the added value if it was not empty, else the unchanged original resource.

        Examples:
            ```python
            resource = resource.add_uri_optional(
                prop_name=":propName",
                value="https://dasch.swiss",
            )
            ```

            ```python
            resource = resource.add_uri_optional(
                prop_name=":propName",
                value=None,
            )
            ```
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
        license: PreDefinedLicense | str,
        copyright_holder: str,
        authorship: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a file (bitstream) to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#bitstream)

        Args:
            filename: path to the file
            license: License of the file (predefined or custom).
                A license states the circumstances how you are allowed to share/reuse something.
            copyright_holder: The person or institution who owns the economic rights of something.
            authorship: The (natural) person who authored something.
            permissions: optional permissions of this file
            comment: optional comment

        Raises:
            InputError: If the resource already has a file or IIIF URI value

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_file(
                filename="images/dog.jpg",
                license=xmllib.PreDefinedLicense.PUBLIC_DOMAIN,
                copyright_holder="Bark University",
                authorship=["Bark McDog"],
            )
            ```

            ```python
            # a file with restricted view permissions
            resource = resource.add_file(
                filename="images/dog.jpg",
                license=xmllib.PreDefinedLicense.PUBLIC_DOMAIN,
                copyright_holder="Bark University",
                authorship=["Bark McDog"],
                permissions=xmllib.Permissions.RESTRICTED_VIEW,
            )
            ```
        """
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name '{filename}' cannot be added."
            )

        fixed_authors = set(check_and_fix_collection_input(authorship, "iiif-uri", self.res_id))
        fixed_authors_list = [str(x).strip() for x in fixed_authors]
        fixed_authors_list = sorted(fixed_authors_list)
        meta = Metadata(
            license=str(license),
            copyright_holder=copyright_holder,
            authorship=tuple(fixed_authors_list),
            permissions=permissions,
            resource_id=self.res_id,
        )
        self.file_value = FileValue(value=filename, metadata=meta, comment=comment, resource_id=self.res_id)
        return self

    def add_iiif_uri(
        self,
        iiif_uri: str,
        license: PreDefinedLicense | str,
        copyright_holder: str,
        authorship: list[str],
        permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS,
        comment: str | None = None,
    ) -> Resource:
        """
        Add a IIIF URI to the resource.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#iiif-uri)

        Args:
            iiif_uri: valid IIIF URI
            license: License of the file (predefined or custom).
                A license states the circumstances how you are allowed to share/reuse something.
            copyright_holder: The person or institution who owns the economic rights of something.
            authorship: The (natural) person who authored something.
            permissions: optional permissions of this file
            comment: optional comment

        Raises:
            InputError: If the resource already has a file or IIIF URI value

        Returns:
            The original resource, with the added value

        Examples:
            ```python
            resource = resource.add_iiif_uri(
                iiif_uri="https://iiif.wellcomecollection.org/image/b20432033_B0008608.JP2/full/1338%2C/0/default.jpg",
                license=xmllib.PreDefinedLicense.CC_BY_NC,
                copyright_holder="Wellcome Collection",
                authorship=["Cavanagh, Annie"]
            )
            ```
        """
        if self.file_value:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains a file with the name: "
                f"'{self.file_value.value}'.\n"
                f"The new file with the name '{iiif_uri}' cannot be added."
            )
        fixed_authors = set(check_and_fix_collection_input(authorship, "iiif-uri", self.res_id))
        fixed_authors_list = [str(x).strip() for x in fixed_authors]
        fixed_authors_list = sorted(fixed_authors_list)
        meta = Metadata(
            license=str(license),
            copyright_holder=copyright_holder,
            authorship=tuple(fixed_authors_list),
            permissions=permissions,
            resource_id=self.res_id,
        )
        self.file_value = IIIFUri(value=iiif_uri, metadata=meta, comment=comment, resource_id=self.res_id)
        return self

    #######################
    # Migration Metadata
    #######################

    def add_migration_metadata(
        self, creation_date: str | None, iri: str | None = None, ark: str | None = None
    ) -> Resource:
        """
        Add metadata from a SALSAH migration.

        [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-resources-with-the-resource-element)

        Args:
            creation_date: creation date of the resource in SALSAH
            iri: Original IRI in SALSAH
            ark: Original ARK in SALSAH

        Raises:
            InputError: if metadata already exists

        Returns:
            The original resource, with the added migration metadata

        Examples:
            ```python
            resource = resource.add_migration_metadata(
                iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```

            ```python
            resource = resource.add_migration_metadata(
                ark="ark:/72163/4123-43xc6ivb931-a.2022829",
                creation_date="1999-12-31T23:59:59.9999999+01:00"
            )
            ```
        """
        if self.migration_metadata:
            raise InputError(
                f"The resource with the ID '{self.res_id}' already contains migration metadata, "
                f"no new data can be added."
            )
        self.migration_metadata = MigrationMetadata(creation_date=creation_date, iri=iri, ark=ark, res_id=self.res_id)
        return self
