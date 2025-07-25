import copy
import dataclasses
import difflib
import json
import os
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import regex
from lxml import etree
from lxml.builder import E

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.data_formats.date_util import is_full_date
from dsp_tools.utils.data_formats.shared import check_notna
from dsp_tools.utils.data_formats.shared import simplify_name
from dsp_tools.utils.data_formats.uri_util import is_iiif_uri
from dsp_tools.utils.data_formats.uri_util import is_uri
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file
from dsp_tools.xmllib.helpers import find_dates_in_string as find_dates_in_string  # noqa: PLC0414 (explicit re-export)
from dsp_tools.xmllib.helpers import make_xsd_compatible_id
from dsp_tools.xmllib.helpers import make_xsd_compatible_id_with_uuid
from dsp_tools.xmllib.internal.input_converters import numeric_entities

# ruff: noqa: E501, UP031 (line-too-long, use f-string over percent formatting)

make_xsd_id_compatible = make_xsd_compatible_id_with_uuid
make_xsd_id_compatible_without_uuid = make_xsd_compatible_id

xml_namespace_map = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}


def prepare_value(
    value: Union[PropertyElement, str, int, float, bool, Iterable[Union[PropertyElement, str, int, float, bool]]],
) -> list[PropertyElement]:
    """
    This method transforms the parameter "value" from a make_*_prop() method into a list of PropertyElements. "value" is
    passed on to this method as it was received.

    Args:
        value: "value" as received from the caller

    Returns:
        a list of PropertyElements
    """
    # make sure that "value" is list-like
    if not isinstance(value, Iterable) or isinstance(value, str):
        value = [value]

    # make a PropertyElement out of its elements, if necessary.
    return [x if isinstance(x, PropertyElement) else PropertyElement(x) for x in value]


def make_root(
    shortcode: str,
    default_ontology: str,
) -> etree._Element:
    """
    Start building your XML document by creating the root element `<knora>`.

    Args:
        shortcode: The shortcode of this project as defined in the JSON project file
        default_ontology: one of the ontologies of the JSON project file

    Returns:
        The root element `<knora>`.

    Examples:
        >>> root = excel2xml.make_root(shortcode=shortcode, default_ontology=default_ontology)
        >>> root = excel2xml.append_permissions(root)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#the-root-element-knora
    """
    schema_url = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd"
    schema_location_key = str(etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"))
    schema_location_value = f"https://dasch.swiss/schema {schema_url}"
    return etree.Element(
        "{%s}knora" % xml_namespace_map[None],
        attrib={
            schema_location_key: schema_location_value,
            "shortcode": shortcode,
            "default-ontology": default_ontology,
        },
        nsmap=xml_namespace_map,
    )


def append_permissions(root_element: etree._Element) -> etree._Element:
    """
    After having created a root element, call this function to append the standard permission definitions "public",
    "limited_view", and "private" to it. These definitions are a good basis to
    start with, but remember that they can be adapted, and that other permissions can be defined instead of these.

    Args:
        root_element: The XML root element `<knora>` created by make_root()

    Returns:
        The root element with the permission definition blocks appended

    Examples:
        >>> root = excel2xml.make_root(shortcode=shortcode, default_ontology=default_ontology)
        >>> root = excel2xml.append_permissions(root)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-permissions-with-permissions-elements
    """

    PERMISSIONS = E.permissions
    ALLOW = E.allow
    # lxml.builder.E is a more sophisticated element factory than etree.Element.
    # E.tag is equivalent to E("tag") and results in <tag>

    _public = PERMISSIONS(id="public")
    _public.append(ALLOW("V", group="UnknownUser"))
    _public.append(ALLOW("V", group="KnownUser"))
    _public.append(ALLOW("D", group="ProjectMember"))
    _public.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(_public)

    _private_view = PERMISSIONS(id="limited_view")
    _private_view.append(ALLOW("RV", group="UnknownUser"))
    _private_view.append(ALLOW("RV", group="KnownUser"))
    _private_view.append(ALLOW("D", group="ProjectMember"))
    _private_view.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(_private_view)

    _private = PERMISSIONS(id="private")
    _private.append(ALLOW("D", group="ProjectMember"))
    _private.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(_private)

    return root_element


def make_resource(  # noqa: D417 (undocumented-param)
    label: str,
    restype: str,
    id: str,
    permissions: str = "public",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty resource element, with the attributes as specified by the arguments.

    Args:
        The arguments correspond to the attributes of the `<resource>` element.

    Returns:
        The resource element, without any children, but with the attributes
        ``<resource label=label restype=restype id=id permissions=permissions ark=ark iri=iri></resource>``

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Examples:
        >>> resource = excel2xml.make_resource(...)
        >>> resource.append(excel2xml.make_text_prop(...))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-resources-with-the-resource-element
    """
    if not check_notna(label):
        msg = f"Your resource's label looks suspicious (resource with id '{id}' and label '{label}')"
        warnings.warn(DspToolsUserWarning(msg))
    if not check_notna(id):
        msg = f"Your resource's id looks suspicious (resource with id '{id}' and label '{label}'"
        warnings.warn(DspToolsUserWarning(msg))
    kwargs = {"label": label, "restype": restype, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        msg = f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI."
        warnings.warn(DspToolsUserWarning(msg))
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The resource '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    return etree.Element("{%s}resource" % xml_namespace_map[None], **kwargs)  # type: ignore[arg-type]


def make_bitstream_prop(
    path: Union[str, os.PathLike[Any]],
    permissions: str = "public",
    check: bool = False,
    calling_resource: str = "",
) -> etree._Element:
    """
    Creates a bitstream element that points to "path".

    Args:
        path: path to a valid file that will be uploaded
        permissions: permissions string
        check: if True, issue a warning if the path doesn't point to an existing file
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        if the path doesn't point to an existing file (only if check=True)

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = excel2xml.make_resource(...)
        >>> resource.append(excel2xml.make_bitstream_prop("data/images/tree.jpg"))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#bitstream
    """

    if check and not Path(path).is_file():
        msg = (
            f"Failed validation in bitstream tag of resource '{calling_resource}': "
            f"The following path doesn't point to a file: {path}"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop_ = etree.Element(
        "{%s}bitstream" % xml_namespace_map[None],
        permissions=permissions,
        nsmap=xml_namespace_map,
    )
    prop_.text = str(path)
    return prop_


def make_iiif_uri_prop(
    iiif_uri: str,
    permissions: str = "public",
    calling_resource: str = "",
) -> etree._Element:
    """
    Creates a iiif-uri element that points to "path".

    Args:
        iiif_uri: URI to a IIIF image
        permissions: permissions string
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the iiif_uri doesn't conform to the IIIF URI specifications

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = excel2xml.make_resource(...)
        >>> resource.append(excel2xml.make_iiif_uri_prop("https://example.org/image-service/abcd1234/full/max/0/default.jpg"))
        >>> root.append(resource)

    """

    if not is_iiif_uri(iiif_uri):
        msg = (
            f"Failed validation in iiif-uri tag of resource '{calling_resource}': "
            f"The URI: '{iiif_uri}' does not conform to the specifications."
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop_ = etree.Element(
        "{%s}iiif-uri" % xml_namespace_map[None],
        permissions=permissions,
        nsmap=xml_namespace_map,
    )
    prop_.text = iiif_uri
    return prop_


def _format_bool(
    unformatted: Union[bool, str, int, float],
    name: str,
    calling_resource: str,
) -> str:
    """
    This method takes an unformatted boolean-like value, and transforms it into the string values "true" or "false".

    Args:
        unformatted: boolean-like value
        name: property name, for better error messages
        calling_resource: resource name, for better error messages

    Raises:
        BaseError: if the input cannot be transformed into "true"/"false"

    Returns:
        "true" if the input is in (True, "true", "1", 1, "yes"); "false" if input is in (False, "false", "0", 0, "no")
    """
    if isinstance(unformatted, str):
        unformatted = unformatted.lower()
    if unformatted in (False, "false", "0", 0, 0.0, "no"):
        return "false"
    elif unformatted in (True, "true", "1", 1, 1.0, "yes"):
        return "true"
    else:
        raise BaseError(
            f"Failed validation in resource '{calling_resource}', property '{name}': "
            f"'{unformatted}' is not a valid boolean."
        )


def make_boolean_prop(
    name: str,
    value: Union[PropertyElement, str, int, bool],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<boolean-prop>` from a boolean value. The value can be provided directly or inside a PropertyElement. The
    following formats are supported:
     - true: (True, "true", "True", "1", 1, "yes", "Yes")
     - false: (False, "false", "False", "0", 0, "no", "No")

    Unless provided as PropertyElement, the permissions of the value default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: a boolean value as str/bool/int, or as str/bool/int inside a PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: if the value is not a valid boolean

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_boolean_prop(":testproperty", "no")
                <boolean-prop name=":testproperty">
                    <boolean permissions="public">false</boolean>
                </boolean-prop>
        >>> excel2xml.make_boolean_prop(":testproperty", excel2xml.PropertyElement("1", permissions="private", comment="example"))
                <boolean-prop name=":testproperty">
                    <boolean permissions="private" comment="example">true</boolean>
                </boolean-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean-prop
    """

    # validate input
    if isinstance(value, PropertyElement):
        value_new = dataclasses.replace(value, value=_format_bool(value.value, name, calling_resource))
    elif isinstance(value, str | bool | int):
        value_new = PropertyElement(_format_bool(value, name, calling_resource))
    else:
        raise BaseError(
            f"Failed validation in resource '{calling_resource}', property '{name}': '{value}' is not a valid boolean."
        )

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}boolean-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    kwargs = {"permissions": value_new.permissions}
    if value_new.comment and check_notna(value_new.comment):
        kwargs["comment"] = value_new.comment
    value_ = etree.Element(
        "{%s}boolean" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
        nsmap=xml_namespace_map,
    )
    value_.text = str(value_new.value)
    prop_.append(value_)

    return prop_


def make_color_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<color-prop>` from one or more colors. The color(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the permissions default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP color(s), as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid color

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_color_prop(":testproperty", "#00ff66")
                <color-prop name=":testproperty">
                    <color permissions="public">#00ff66</color>
                </color-prop>
        >>> excel2xml.make_color_prop(":testproperty", excel2xml.PropertyElement("#00ff66", permissions="private", comment="example"))
                <color-prop name=":testproperty">
                    <color permissions="private" comment="example">#00ff66</color>
                </color-prop>
        >>> excel2xml.make_color_prop(":testproperty", ["#00ff66", "#000000"])
                <color-prop name=":testproperty">
                    <color permissions="public">#00ff66</color>
                    <color permissions="public">#000000</color>
                </color-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not regex.search(r"^#[0-9a-f]{6}$", str(val.value).strip(), flags=regex.IGNORECASE):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid color."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}color-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}color" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value).strip()
        prop_.append(value_)

    return prop_


def make_date_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<date-prop>` from one or more dates/date ranges. The date(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permissions default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP dates, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid DSP date

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_date_prop(":testproperty", "GREGORIAN:CE:2014-01-31")
                <date-prop name=":testproperty">
                    <date permissions="public">GREGORIAN:CE:2014-01-31</date>
                </date-prop>
        >>> excel2xml.make_date_prop(":testproperty", excel2xml.PropertyElement("GREGORIAN:CE:2014-01-31", permissions="private", comment="example"))
                <date-prop name=":testproperty">
                    <date permissions="private" comment="example">
                        GREGORIAN:CE:2014-01-31
                    </date>
                </date-prop>
        >>> excel2xml.make_date_prop(":testproperty", ["GREGORIAN:CE:1930-09-02:CE:1930-09-03", "GREGORIAN:CE:1930-09-02:CE:1930-09-03"])
                <date-prop name=":testproperty">
                    <date permissions="public">
                        GREGORIAN:CE:1930-09-02:CE:1930-09-03
                    </date>
                    <date permissions="public">
                        GREGORIAN:CE:1930-09-02:CE:1930-09-03
                    </date>
                </date-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not is_full_date(str(val.value).strip()):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid DSP date."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}date-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}date" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value).strip()
        prop_.append(value_)

    return prop_


def make_decimal_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<decimal-prop>` from one or more decimal numbers. The decimal(s) can be provided as string, float, or as
    PropertyElement with a string/float inside. If provided as string/float, the permissions default to
    "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more decimal numbers, as string/float/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid decimal number

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_decimal_prop(":testproperty", "3.14159")
                <decimal-prop name=":testproperty">
                    <decimal permissions="public">3.14159</decimal>
                </decimal-prop>
        >>> excel2xml.make_decimal_prop(":testproperty", excel2xml.PropertyElement("3.14159", permissions="private", comment="example"))
                <decimal-prop name=":testproperty">
                    <decimal permissions="private" comment="example">3.14159</decimal>
                </decimal-prop>
        >>> excel2xml.make_decimal_prop(":testproperty", ["3.14159", "2.718"])
                <decimal-prop name=":testproperty">
                    <decimal permissions="public">3.14159</decimal>
                    <decimal permissions="public">2.718</decimal>
                </decimal-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#decimal-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            float(val.value)
        except ValueError:
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid decimal number."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}decimal-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}decimal" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_geometry_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<geometry-prop>` from one or more areas of an image. The area(s) can be provided as JSON-string or as
    PropertyElement with the JSON-string inside. If provided as string, the permissions default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more JSON geometry objects, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid JSON geometry object

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_geometry_prop(":testproperty", json_string)
                <geometry-prop name=":testproperty">
                    <geometry permissions="public">{JSON}</geometry>
                </geometry-prop>
        >>> excel2xml.make_geometry_prop(":testproperty", excel2xml.PropertyElement(json_string, permissions="private", comment="example"))
                <geometry-prop name=":testproperty">
                    <geometry permissions="private" comment="example">{JSON}</geometry>
                </geometry-prop>
        >>> excel2xml.make_geometry_prop(":testproperty", [json_string1, json_string2])
                <geometry-prop name=":testproperty">
                    <geometry permissions="public">{JSON}</geometry>
                    <geometry permissions="public">{JSON}</geometry>
                </geometry-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geometry-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            value_as_dict = json.loads(str(val.value))
            if value_as_dict["type"] not in ["rectangle", "circle", "polygon"]:
                msg = (
                    f"Failed validation in resource '{calling_resource}', property '{name}': "
                    f"The 'type' of the JSON geometry object must be 'rectangle', 'circle', or 'polygon'."
                )
                warnings.warn(DspToolsUserWarning(msg))
            if not isinstance(value_as_dict["points"], list):
                msg = (
                    f"Failed validation in resource '{calling_resource}', property '{name}': "
                    f"The 'points'of the JSON geometry object must be a list of points."
                )
                warnings.warn(DspToolsUserWarning(msg))
        except (json.JSONDecodeError, TypeError, IndexError, KeyError, AssertionError):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid JSON geometry object."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}geometry-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}geometry" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)
    return prop_


def make_geoname_prop(
    name: str,
    value: Union[PropertyElement, str, int, Iterable[Union[PropertyElement, str, int]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<geoname-prop>` from one or more geonames.org IDs. The ID(s) can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more geonames.org IDs, as str/int/PropertyElement, or as iterable of str/int/PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid geonames.org identifier

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_geoname_prop(":testproperty", "2761369")
                <geoname-prop name=":testproperty">
                    <geoname permissions="public">2761369</geoname>
                </geoname-prop>
        >>> excel2xml.make_geoname_prop(":testproperty", excel2xml.PropertyElement("2761369", permissions="private", comment="example"))
                <geoname-prop name=":testproperty">
                    <geoname permissions="private" comment="example">2761369</geoname>
                </geoname-prop>
        >>> excel2xml.make_geoname_prop(":testproperty", ["2761369", "1010101"])
                <geoname-prop name=":testproperty">
                    <geoname permissions="public">2761369</geoname>
                    <geoname permissions="public">1010101</geoname>
                </geoname-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not regex.search(r"^[0-9]+$", str(val.value)):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a geonames.org identifier."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}geoname-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}geoname" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_integer_prop(
    name: str,
    value: Union[PropertyElement, str, int, Iterable[Union[PropertyElement, str, int]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<integer-prop>` from one or more integers. The integers can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more integers, as string/int/PropertyElement, or as iterable of strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the value is not a valid integer

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_integer_prop(":testproperty", "2761369")
                <integer-prop name=":testproperty">
                    <integer permissions="public">2761369</integer>
                </integer-prop>
        >>> excel2xml.make_integer_prop(":testproperty", excel2xml.PropertyElement("2761369", permissions="private", comment="example"))
                <integer-prop name=":testproperty">
                    <integer permissions="private" comment="example">2761369</integer>
                </integer-prop>
        >>> excel2xml.make_integer_prop(":testproperty", ["2761369", "1010101"])
                <integer-prop name=":testproperty">
                    <integer permissions="public">2761369</integer>
                    <integer permissions="public">1010101</integer>
                </integer-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#integer-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            int(val.value)
        except ValueError:
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid integer."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}integer-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}integer" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_list_prop(
    list_name: str,
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<list-prop>` from one or more list nodes. The name(s) of the list node(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "public".

    Args:
        list_name: the name of the list as defined in the onto
        name: the name of this property as defined in the onto
        value: one or more node names, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the name of one of the list nodes is not a valid string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_list_prop("mylist", ":testproperty", "first_node")
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="public">first_node</list>
                </list-prop>
        >>> excel2xml.make_list_prop("mylist", ":testproperty", excel2xml.PropertyElement("first_node", permissions="private", comment="example"))
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="private" comment="example">first_node</list>
                </list-prop>
        >>> excel2xml.make_list_prop("mylist", ":testproperty", ["first_node", "second_node"])
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="public">first_node</list>
                    <list permissions="public">second_node</list>
                </list-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid name of a list node."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}list-prop" % xml_namespace_map[None],
        list=list_name,
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}list" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_resptr_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<resptr-prop>` from one or more IDs of other resources. The ID(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more resource identifiers, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If the ID of one of the target resources is not a valid string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_resptr_prop(":testproperty", "resource_1")
                <resptr-prop name=":testproperty">
                    <resptr permissions="public">resource_1</resptr>
                </resptr-prop>
        >>> excel2xml.make_resptr_prop(":testproperty", excel2xml.PropertyElement("resource_1", permissions="private", comment="example"))
                <resptr-prop name=":testproperty">
                    <resptr permissions="private" comment="example">resource_1</resptr>
                </resptr-prop>
        >>> excel2xml.make_resptr_prop(":testproperty", ["resource_1", "resource_2"])
                <resptr-prop name=":testproperty">
                    <resptr permissions="public">resource_1</resptr>
                    <resptr permissions="public">resource_2</resptr>
                </resptr-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            msg = (
                f"Validation Error in resource '{calling_resource}', property '{name}': "
                f"The following doesn't seem to be a valid ID of a target resource: '{val.value}'"
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}resptr-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}resptr" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_text_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<text-prop>` from one or more strings. The string(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the encoding defaults to utf8, and the permissions to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more strings, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: if the XML tags in a richtext property (encoding=xml) are not well-formed
        Warning: if one of the values doesn't look like a reasonable string
            (e.g. `<NA>` is a valid string, but probably not intended)

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="public">first text</text>
                </text-prop>
        >>> excel2xml.make_text_prop(":testproperty", excel2xml.PropertyElement("first text", permissions="private", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="private">first text</text>
                </text-prop>
        >>> excel2xml.make_text_prop(":testproperty", ["first text", "second text"])
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="public">first text</text>
                    <text encoding="utf8" permissions="public">second text</text>
                </text-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is probably not a usable string."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}text-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        kwargs["encoding"] = val.encoding if check_notna(val.encoding) else "utf8"
        value_ = etree.Element(
            "{%s}text" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        if kwargs["encoding"] == "utf8":
            # write the text into the tag, without validation
            value_.text = str(val.value)
        else:
            try:
                value_ = _add_richtext_to_etree_element(str(val.value), value_)
            except BaseError as err:
                if calling_resource:
                    err.message += f"The error occurred in resource {calling_resource}, property {name}"
                raise err from None
        prop_.append(value_)

    return prop_


def _add_richtext_to_etree_element(richtext: str, element: etree._Element) -> etree._Element:
    new_element = copy.deepcopy(element)
    escaped_text = _escape_reserved_chars(richtext)
    num_ent = numeric_entities(escaped_text)
    pseudo_xml = f"<ignore-this>{num_ent}</ignore-this>"
    try:
        parsed = etree.fromstring(pseudo_xml)
    except etree.XMLSyntaxError as err:
        msg = (
            "The XML tags contained in a richtext property (encoding=xml) must be well-formed. "
            "The special characters <, > and & are only allowed to construct a tag. "
        )
        msg += f"\nOriginal error message: {err.msg}"
        msg += f"\nEventual line/column numbers are relative to this text: {pseudo_xml}"
        raise BaseError(msg) from None
    new_element.text = parsed.text  # everything before the first child tag
    new_element.extend(list(parsed))  # all (nested) children of the pseudo-xml
    return new_element


def _escape_reserved_chars(text: str) -> str:
    """
    From richtext strings (encoding="xml"), escape the reserved characters <, > and &,
    but only if they are not part of a standard standoff tag or escape sequence.
    The standard standoff tags allowed by DSP-API are documented here:
    https://docs.dasch.swiss/2023.12.01/DSP-API/03-endpoints/api-v2/text/standard-standoff/

    Args:
        text: the richtext string to be escaped

    Returns:
        the escaped richtext string
    """
    allowed_tags = [
        "a( [^>]+)?",  # <a> is the only tag that can have attributes
        "p",
        "em",
        "strong",
        "u",
        "sub",
        "sup",
        "strike",
        "h1",
        "ol",
        "ul",
        "li",
        "tbody",
        "table",
        "tr",
        "td",
        "br",
        "hr",
        "pre",
        "cite",
        "blockquote",
        "code",
    ]
    allowed_tags_regex = "|".join(allowed_tags)
    lookahead = rf"(?!/?({allowed_tags_regex})/?>)"
    illegal_lt = rf"<{lookahead}"
    lookbehind = rf"(?<!</?({allowed_tags_regex})/?)"
    illegal_gt = rf"{lookbehind}>"
    illegal_amp = r"&(?![#a-zA-Z0-9]+;)"
    text = regex.sub(illegal_lt, "&lt;", text)
    text = regex.sub(illegal_gt, "&gt;", text)
    text = regex.sub(illegal_amp, "&amp;", text)
    return text


def make_time_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<time-prop>` from one or more datetime values of the form "2009-10-10T12:00:00-05:00". The time(s) can be
    provided as string or as PropertyElement with a string inside. If provided as string, the permissions default to
    "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP times, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If one of the values is not a valid DSP time string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_time_prop(":testproperty", "2009-10-10T12:00:00-05:00")
                <time-prop name=":testproperty">
                    <time permissions="public">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> excel2xml.make_time_prop(":testproperty", excel2xml.PropertyElement("2009-10-10T12:00:00-05:00", permissions="private", comment="example"))
                <time-prop name=":testproperty">
                    <time permissions="private" comment="example">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> excel2xml.make_time_prop(":testproperty", ["2009-10-10T12:00:00-05:00", "1901-01-01T01:00:00-00:00"])
                <time-prop name=":testproperty">
                    <time permissions="public">
                        2009-10-10T12:00:00-05:00
                    </time>
                    <time permissions="public">
                        1901-01-01T01:00:00-00:002
                    </time>
                </time-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#time-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    validation_regex = r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$"
    for val in values:
        if not regex.search(validation_regex, str(val.value)):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid DSP time."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}time-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}time" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_uri_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make an `<uri-prop>` from one or more URIs. The URI(s) can be provided as string or as PropertyElement with a string
    inside. If provided as string, the permissions default to "public".

    Args:
        name: the name of this property as defined in the onto
        value: one or more URIs, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        If one of the values is not a valid URI

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> excel2xml.make_uri_prop(":testproperty", "www.test.com")
                <uri-prop name=":testproperty">
                    <uri permissions="public">www.test.com</uri>
                </uri-prop>
        >>> excel2xml.make_uri_prop(":testproperty", excel2xml.PropertyElement("www.test.com", permissions="private", comment="example"))
                <uri-prop name=":testproperty">
                    <uri permissions="private" comment="example">www.test.com</uri>
                </uri-prop>
        >>> excel2xml.make_uri_prop(":testproperty", ["www.1.com", "www.2.com"])
                <uri-prop name=":testproperty">
                    <uri permissions="public">www.1.com</uri>
                    <uri permissions="public">www.2.com</uri>
                </uri-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not is_uri(str(val.value)):
            msg = (
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid URI."
            )
            warnings.warn(DspToolsUserWarning(msg))

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}uri-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}uri" % xml_namespace_map[None],
            **kwargs,  # type: ignore[arg-type]
            nsmap=xml_namespace_map,
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_region(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
    permissions: str = "public",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty region element, with the attributes as specified by the arguments.

    Args:
        The arguments correspond 1:1 to the attributes of the `<region>` element.

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Returns:
        The region element, without any children, but with the attributes
        `<region label=label id=id permissions=permissions ark=ark iri=iri></region>`

    Examples:
        >>> region = excel2xml.make_region("label", "id")
        >>> region.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
        >>> region.append(excel2xml.make_color_prop("hasColor", "#5d1f1e"))
        >>> region.append(excel2xml.make_resptr_prop("isRegionOf", "image_0"))
        >>> region.append(excel2xml.make_geometry_prop("hasGeometry", "{...}"))
        >>> root.append(region)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#region
    """

    kwargs = {"label": label, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        msg = f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI."
        warnings.warn(DspToolsUserWarning(msg))
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The region '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    return etree.Element(
        "{%s}region" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )


def make_link(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
    permissions: str = "public",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty link element, with the attributes as specified by the arguments.

    Args:
        The arguments correspond 1:1 to the attributes of the `<link>` element.

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Returns:
        The link element, without any children, but with the attributes
        `<link label=label id=id permissions=permissions ark=ark iri=iri></link>`

    Examples:
        >>> link = excel2xml.make_link("label", "id")
        >>> link.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
        >>> link.append(excel2xml.make_resptr_prop("hasLinkTo", ["resource_0", "resource_1"]))
        >>> root.append(link)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#link
    """

    kwargs = {"label": label, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        msg = f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI."
        warnings.warn(DspToolsUserWarning(msg))
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The link '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    return etree.Element(
        "{%s}link" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )


def make_audio_segment(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
    permissions: str = "public",
) -> etree._Element:
    """
    Creates an empty `<audio-segment>` element, with the attributes as specified by the arguments.

    Args:
        The arguments correspond 1:1 to the attributes of the `<audio-segment>` element.

    Returns:
        The audio-segment element, without any children, but with the attributes
        `<audio-segment label=label id=id permissions=permissions></audio-segment>`

    Examples:
        >>> audio_segment = excel2xml.make_audio_segment("label", "id")
        >>> audio_segment.append(excel2xml.make_isSegmentOf_prop("audio_resource_id"))
        >>> audio_segment.append(excel2xml.make_hasSegmentBounds_prop(segment_start=60, segment_end=120)
        >>> root.append(audio_segment)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#video-segment-audio-segment
    """
    return etree.Element(
        "{%s}audio-segment" % xml_namespace_map[None],
        label=label,
        id=id,
        permissions=permissions,
        nsmap=xml_namespace_map,
    )


def make_video_segment(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
    permissions: str = "public",
) -> etree._Element:
    """
    Creates an empty `<video-segment>` element, with the attributes as specified by the arguments.

    Args:
        The arguments correspond 1:1 to the attributes of the `<video-segment>` element.

    Returns:
        The video-segment element, without any children, but with the attributes
        `<video-segment label=label id=id permissions=permissions></video-segment>`

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_isSegmentOf_prop("video_resource_id"))
        >>> video_segment.append(excel2xml.make_hasSegmentBounds_prop(segment_start=60, segment_end=120)
        >>> root.append(video_segment)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#video-segment-audio-segment
    """
    return etree.Element(
        "{%s}video-segment" % xml_namespace_map[None],
        label=label,
        id=id,
        permissions=permissions,
        nsmap=xml_namespace_map,
    )


def make_isSegmentOf_prop(
    target_id: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<isSegmentOf>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        target_id: ID of target video/audio resource
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the target_id is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_isSegmentOf_prop("video_resource_id"))
        >>> video_segment.append(excel2xml.make_hasSegmentBounds_prop(segment_start=60, segment_end=120)
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video segment with `segment.append(make_isSegmentOf_prop(...))`
    """
    if not isinstance(target_id, str) or not check_notna(target_id):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'isSegmentOf': "
            f"The following doesn't seem to be a valid ID of a target resource: '{target_id}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}isSegmentOf" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop.text = target_id
    return prop


def make_relatesTo_prop(
    target_id: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<relatesTo>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        target_id: ID of the related resource
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the target_id is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_relatesTo_prop("resource_id"))
        >>> video_segment.append(excel2xml.make_relatesTo_prop("other_resource_id")
        >>> # add other properties
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video segment with `segment.append(make_relatesTo_prop(...))`
    """
    if not isinstance(target_id, str) or not check_notna(target_id):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'relatesTo': "
            f"The following doesn't seem to be a valid ID of a target resource: '{target_id}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}relatesTo" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop.text = target_id
    return prop


def make_hasSegmentBounds_prop(
    segment_start: int | float,
    segment_end: int | float,
    permissions: str = "public",
    comment: str | None = None,
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a `<hasSegmentBounds>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        segment_start: start, in seconds, counted from the beginning of the audio/video
        segment_end: end, in seconds, counted from the beginning of the audio/video
        permissions: Defaults to "public".
        comment: Optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If start or end are not integers or floats
        - If start is bigger than end

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_isSegmentOf_prop("video_resource_id"))
        >>> video_segment.append(excel2xml.make_hasSegmentBounds_prop(segment_start=60, segment_end=120)
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video segment with `segment.append(make_hasSegmentBounds_prop(...))`
    """
    if not isinstance(segment_start, int | float) or not isinstance(segment_end, int | float):
        try:
            segment_start = float(segment_start)
            segment_end = float(segment_end)
        except ValueError:
            msg = (
                f"Validation Error in resource '{calling_resource}', property 'hasSegmentBounds': "
                f"The start and the end of an audio/video segment must be integers or floats, "
                f"but you provided: {segment_start=} and {segment_end=}"
            )
            warnings.warn(DspToolsUserWarning(msg))
    if isinstance(segment_start, int | float) and isinstance(segment_end, int | float) and segment_start > segment_end:
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'hasSegmentBounds': "
            f"The start of an audio/video segment must be less than the end, "
            f"but you provided: {segment_start=} and {segment_end=}"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element(
        "{%s}hasSegmentBounds" % xml_namespace_map[None],
        segment_start=str(segment_start),
        segment_end=str(segment_end),
        permissions=permissions,
    )
    if comment:
        prop.set("comment", comment)
    return prop


def make_hasTitle_prop(
    title: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<hasTitle>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        title: the title of the segment
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the title is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_hasTitle_prop("title of my segment"))
        >>> # add other properties
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video resource with `segment.append(make_hasTitle_prop(...))`
    """
    if not isinstance(title, str) or not check_notna(title):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'hasTitle': "
            f"The following doesn't seem to be a valid string: '{title}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}hasTitle" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop.text = title
    return prop


def make_hasKeyword_prop(
    keyword: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<hasKeyword>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        keyword: a keyword of the segment
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the keyword is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_hasKeyword_prop("keyword of my segment"))
        >>> video_segment.append(excel2xml.make_hasKeyword_prop("another keyword"))
        >>> # add other properties
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video resource with `segment.append(make_hasKeyword_prop(...))`
    """
    if not isinstance(keyword, str) or not check_notna(keyword):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'hasKeyword': "
            f"The following doesn't seem to be a valid string: '{keyword}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}hasKeyword" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop.text = keyword
    return prop


def make_hasComment_prop(
    comment_text: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<hasComment>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        comment_text: a text with some background info about the segment. Can be formatted with tags.
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the comment text is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_hasComment_prop("comment of my segment"))
        >>> video_segment.append(excel2xml.make_hasComment_prop("another comment"))
        >>> # add other properties
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video resource with `segment.append(make_hasComment_prop(...))`
    """
    if not isinstance(comment_text, str) or not check_notna(comment_text):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'hasComment': "
            f"The following doesn't seem to be a valid string: '{comment_text}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}hasComment" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop = _add_richtext_to_etree_element(comment_text, prop)
    return prop


def make_hasDescription_prop(
    description: str, permissions: str = "public", comment: str | None = None, calling_resource: str = ""
) -> etree._Element:
    """
    Make a `<hasDescription>` property for a `<video-segment>` or `<audio-segment>`.

    Args:
        description: a text with some background info about the segment. Can be formatted with tags.
        permissions: defaults to "public".
        comment: optional comment for this property. Defaults to None.
        calling_resource: the name of the parent resource (for better error messages)

    Warns:
        - If the description is not a valid string

    Examples:
        >>> video_segment = excel2xml.make_video_segment("label", "id")
        >>> video_segment.append(excel2xml.make_hasDescription_prop("a description of my segment"))
        >>> video_segment.append(excel2xml.make_hasDescription_prop("another description"))
        >>> # add other properties
        >>> root.append(video_segment)

    Returns:
        an etree._Element that can be appended to an audio/video resource with `segment.append(make_hasDescription_prop(...))`
    """
    if not isinstance(description, str) or not check_notna(description):
        msg = (
            f"Validation Error in resource '{calling_resource}', property 'hasDescription': "
            f"The following doesn't seem to be a valid string: '{description}'"
        )
        warnings.warn(DspToolsUserWarning(msg))
    prop = etree.Element("{%s}hasDescription" % xml_namespace_map[None], permissions=permissions)
    if comment:
        prop.set("comment", comment)
    prop = _add_richtext_to_etree_element(description, prop)
    return prop


def create_json_excel_list_mapping(
    path_to_json: str,
    list_name: str,
    excel_values: Iterable[str],
    sep: str = '+"*ç%&/()=',
    corrections: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """
    Often, data sources contain list values that aren't identical to the name of the node in the list of the JSON
    project file (colloquially: ontology). In order to create a correct XML for the `dsp-tools xmlupload`, a mapping is
    necessary. This function takes a JSON list and an Excel column containing list-values, and tries to match them
    automatically based on similarity. The result is a dict of the form {excel_value: list_node_name}.

    Alternatively, consider using the function create_json_list_mapping(), which also builds a dictionary,
    but from the names and labels in the JSON list, which is less error-prone than this function's approach. However,
    this function has the advantage that it even works when your data source doesn't use the list labels correctly.

    Args:
        path_to_json: path to the JSON project file
        list_name: name of the list in the JSON project file (can also be a nested list)
        excel_values: the Excel column (e.g. as list) with the list values in it
        sep: separator string, if the cells in the Excel contain more than one list entry
        corrections: dict with wrong entries, each pointing to its correct counterpart

    Raises:
        Warning: if there is an Excel value that couldn't be matched
        Exception: if the path doesn't point to a JSON project file

    Returns:
        dict of the form ``{excel_value: list_node_name}``.
            Every excel_value is stripped, and also present in a lowercase form.

    Examples:
        >>> json_list_nodes = [
                {
                    "name": "giraffe",
                    "labels": {"en": "giraffe"}
                },
                {
                    "name": "antelope",
                    "labels": {"en": "antelope"}
                }
            ]
        >>> excel_row_1 = ["Giraffeeh ", " Antiloupe", "Girraffe , Antiloupe "]
        >>> json_excel_list_mapping = {
                "Giraffeeh": "giraffe",
                "giraffeeh": "giraffe",
                "Girraffe": "giraffe",
                "girraffe": "giraffe",
                "Antiloupe": "antelope",
                "antiloupe": "antelope"
            }
    """

    # avoid mutable default argument
    corrections = corrections or {}

    # split the values, if necessary
    excel_values_new = []
    for val in excel_values:
        if isinstance(val, str):
            excel_values_new.extend([x.strip() for x in val.split(sep) if x.strip()])

    # read the list of the JSON project (works also for nested lists)
    with open(path_to_json, encoding="utf-8") as f:
        json_file = json.load(f)
    json_subset = []
    for elem in json_file["project"]["lists"]:
        if elem["name"] == list_name:
            json_subset = elem["nodes"]
    json_values = set(_nested_dict_values_iterator(json_subset))

    # build dictionary with the mapping, based on string similarity
    res = {}
    for excel_value in excel_values_new:
        excel_value_corrected = corrections.get(excel_value, excel_value)
        excel_value_simpl = simplify_name(excel_value_corrected)  # increase match probability by removing illegal chars
        if matches := difflib.get_close_matches(
            word=excel_value_simpl,
            possibilities=json_values,
            n=1,
            cutoff=0.6,
        ):
            res[excel_value] = matches[0]
            res[excel_value.lower()] = matches[0]
        else:
            msg = (
                f"Did not find a close match to the excel list entry '{excel_value}' "
                f"among the values in the JSON project list '{list_name}'"
            )
            warnings.warn(DspToolsUserWarning(msg))

    return res


def _nested_dict_values_iterator(dicts: list[dict[str, Any]]) -> Iterable[str]:
    """
    Yield all values of a nested dictionary.

    Args:
        dicts: list of nested dictionaries

    Yields:
        values of the nested dictionaries
    """
    # Credits: https://thispointer.com/python-iterate-loop-over-all-nested-dictionary-values/
    for _dict in dicts:
        if "nodes" in _dict:
            yield from _nested_dict_values_iterator(_dict["nodes"])
        if "name" in _dict:
            yield _dict["name"]


def create_json_list_mapping(
    path_to_json: str,
    list_name: str,
    language_label: str,
) -> dict[str, str]:
    """
    Often, data sources contain list values named after the "label" of the JSON project list node, instead of the "name"
    which is needed for the `dsp-tools xmlupload`. In order to create a correct XML, you need a dictionary that maps the
    "labels" to their correct "names".

    Alternatively, consider using the method create_json_excel_list_mapping(), which also creates a dictionary, but maps
    values from your data source to list node names from the JSON project file, based on similarity.

    Args:
        path_to_json: path to a JSON project file (a.k.a. ontology)
        list_name: name of a list in the JSON project (works also for nested lists)
        language_label: which language of the label to choose

    Returns:
        a dictionary of the form {label: name}
    """
    with open(path_to_json, encoding="utf-8") as f:
        json_file = json.load(f)
    json_subset = [x for x in json_file["project"]["lists"] if x["name"] == list_name]
    # json_subset is a list containing one item, namely the json object containing the entire json-list

    res = {}
    for label, name in _name_label_mapper_iterator(json_subset, language_label):
        if name != list_name:
            res[label] = name
            res[label.strip().lower()] = name

    return res


def _name_label_mapper_iterator(
    json_subset: list[dict[str, Any]],
    language_label: str,
) -> Iterable[tuple[str, str]]:
    """
    Go through list nodes of a JSON project and yield (label, name) pairs.

    Args:
        json_subset: list of DSP lists (a DSP list being a dictionary with the keys "name", "labels" and "nodes")
        language_label: which language of the label to choose

    Yields:
        (label, name) pairs
    """
    for node in json_subset:
        # node is the json object containing the entire json-list
        if "nodes" in node:
            # "nodes" is the json sub-object containing the entries of the json-list
            yield from _name_label_mapper_iterator(node["nodes"], language_label)
            # each yielded value is a (label, name) pair of a single list entry
        if "name" in node:
            yield (node["labels"][language_label], node["name"])
            # the actual values of the name and the label


def write_xml(
    root: etree._Element,
    filepath: str | Path,
) -> None:
    """
    Write the finished XML to a file.

    Args:
        root: etree Element with the entire XML document
        filepath: where to save the file

    Warning:
        if the XML is not valid according to the schema
    """
    warn_msg = (
        "The excel2xml lib is deprecated in favor of the xmllib. It will be removed in a future release.\n"
        "See the xmllib docs: https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/xmlroot/"
    )
    warnings.warn(DspToolsUserWarning(warn_msg))
    etree.indent(root, space="    ")
    xml_string = etree.tostring(
        root,
        encoding="unicode",
        pretty_print=True,
        doctype='<?xml version="1.0" encoding="UTF-8"?>',
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_string)
    try:
        parse_and_validate_xml_file(input_file=filepath)
        print(f"The XML file was successfully saved to {filepath}")
    except BaseError as err:
        msg = (
            f"The XML file was successfully saved to {filepath}, "
            f"but the following Schema validation error(s) occurred: {err.message}"
        )
        warnings.warn(DspToolsUserWarning(msg))
