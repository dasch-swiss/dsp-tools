# pylint: disable=line-too-long,consider-using-f-string

from __future__ import annotations

import dataclasses
import datetime
import difflib
import json
import os
import re
import uuid
import warnings
from typing import Any, Callable, Iterable, Optional, Union

import pandas as pd
import regex
from lxml import etree
from lxml.builder import E  # pylint: disable=no-name-in-module

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.helpers import DateTimeStamp

# explicitly export PropertyElement, so that API users can import it from this module
# (see https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-no-implicit-reexport)
# doing this requires silencing the corresponding pylint warning
# (see https://pylint.readthedocs.io/en/latest/user_guide/messages/convention/useless-import-alias.html)
from dsp_tools.models.propertyelement import PropertyElement as PropertyElement  # pylint: disable=useless-import-alias
from dsp_tools.models.value import UriValue
from dsp_tools.utils.shared import check_notna as check_notna  # pylint: disable=useless-import-alias
from dsp_tools.utils.shared import simplify_name as simplify_name  # pylint: disable=useless-import-alias
from dsp_tools.utils.shared import validate_xml_against_schema

xml_namespace_map = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}


def make_xsd_id_compatible(string: str) -> str:
    """
    Make a string compatible with the constraints of xsd:ID, so that it can be used as "id" attribute of a <resource>
    tag. An xsd:ID must not contain special characters, and it must be unique in the document.

    This method replaces the illegal characters by "_" and appends a random component to the string to make it unique.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``), underscore, !, ?, or number,
    but must not be "None", "<NA>", "N/A", or "-". Otherwise, a BaseError will be raised.

    Args:
        string: input string

    Raises:
        BaseError: if the input cannot be transformed to an xsd:ID

    Returns:
        an xsd:ID based on the input string
    """

    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be transformed to an xsd:ID")

    # if start of string is neither letter nor underscore, add an underscore
    res = re.sub(r"^(?=[^A-Za-z_])", "_", string)

    # replace all illegal characters by underscore
    res = re.sub(r"[^\w_\-.]", "_", res, flags=re.ASCII)

    # add uuid
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"

    return res


def find_date_in_string(string: str) -> Optional[str]:
    """
    Checks if a string contains a date value (single date, or date range), and returns the first found date as
    DSP-formatted string. Returns None if no date was found.

    Notes:
        - All dates are interpreted in the Christian era and the Gregorian calendar. There is no support for BC dates or
          non-Gregorian calendars.
        - The years 0000-2999 are supported, in 4-digit form.
        - Dates written with slashes are always interpreted in a European manner: 5/11/2021 is the 5th of November.

    Currently supported date formats:
        - 0476-09-04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 0476_09_04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 30.4.2021 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 5/11/2021 -> GREGORIAN:CE:2021-11-05:CE:2021-11-05
        - Jan 26, 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - February26,2051 -> GREGORIAN:CE:2051-02-26:CE:2051-02-26
        - 28.2.-1.12.1515 --> GREGORIAN:CE:1515-02-28:CE:1515-12-01
        - 25.-26.2.0800 --> GREGORIAN:CE:0800-02-25:CE:0800-02-26
        - 1.9.2022-3.1.2024 --> GREGORIAN:CE:2022-09-01:CE:2024-01-03
        - 1848 -> GREGORIAN:CE:1848:CE:1848
        - 1849/1850 -> GREGORIAN:CE:1849:CE:1850
        - 1849/50 -> GREGORIAN:CE:1849:CE:1850
        - 1845-50 -> GREGORIAN:CE:1845:CE:1850

    Args:
        string: string to check

    Returns:
        DSP-formatted date string, or None

    Examples:
        >>> if find_date_in_string(row["Epoch"]):
        >>>     resource.append(make_date_prop(":hasDate", find_date_in_string(row["Epoch"]))

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date-prop
    """

    # sanitize input, just in case that the method was called on an empty or N/A cell
    if not check_notna(string):
        return None
    string = str(string)

    months_dict = {
        "January": 1,
        "Jan": 1,
        "February": 2,
        "Feb": 2,
        "March": 3,
        "Mar": 3,
        "April": 4,
        "Apr": 4,
        "May": 5,
        "June": 6,
        "Jun": 6,
        "July": 7,
        "Jul": 7,
        "August": 8,
        "Aug": 8,
        "September": 9,
        "Sept": 9,
        "October": 10,
        "Oct": 10,
        "November": 11,
        "Nov": 11,
        "December": 12,
        "Dec": 12,
    }

    startdate: Optional[datetime.date] = None
    enddate: Optional[datetime.date] = None
    startyear: Optional[int] = None
    endyear: Optional[int] = None

    year_regex = r"([0-2][0-9][0-9][0-9])"
    month_regex = r"([0-1]?[0-9])"
    day_regex = r"([0-3]?[0-9])"
    sep_regex = r"[\./]"
    lookbehind = r"(?<![0-9A-Za-z])"
    lookahead = r"(?![0-9A-Za-z])"

    # template: 2021-01-01 | 2015_01_02
    iso_date = re.search(rf"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}", string)
    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range_regex = (
        rf"{lookbehind}"
        rf"{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex}?)? ?(?:-|:|to) ?"
        rf"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex}"
        rf"{lookahead}"
    )
    eur_date_range = re.search(eur_date_range_regex, string)
    # template: 1.4.2021 | 5/11/2021
    eur_date = re.search(rf"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex}{lookahead}", string)
    # template: March 9, 1908 | March5,1908 | May 11, 1906
    all_months = "|".join(months_dict)
    monthname_date_regex = rf"{lookbehind}({all_months}) ?{day_regex}, ?{year_regex}{lookahead}"
    monthname_date = re.search(monthname_date_regex, string)
    # template: 1849/50 | 1849-50 | 1849/1850
    year_range = re.search(lookbehind + year_regex + r"[/-](\d{2}|\d{4})" + lookahead, string)
    # template: 1907
    year_only = re.search(rf"{lookbehind}{year_regex}{lookahead}", string)

    if iso_date:
        year = int(iso_date.group(1))
        month = int(iso_date.group(2))
        day = int(iso_date.group(3))
        try:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        except ValueError:
            return None

    elif eur_date_range:
        startday = int(eur_date_range.group(1))
        startmonth = int(eur_date_range.group(2)) if eur_date_range.group(2) else int(eur_date_range.group(5))
        startyear = int(eur_date_range.group(3)) if eur_date_range.group(3) else int(eur_date_range.group(6))
        endday = int(eur_date_range.group(4))
        endmonth = int(eur_date_range.group(5))
        endyear = int(eur_date_range.group(6))
        try:
            startdate = datetime.date(startyear, startmonth, startday)
            enddate = datetime.date(endyear, endmonth, endday)
            if enddate < startdate:
                raise ValueError
        except ValueError:
            return None

    elif eur_date:
        startday = int(eur_date.group(1))
        startmonth = int(eur_date.group(2))
        startyear = int(eur_date.group(3))
        try:
            startdate = datetime.date(startyear, startmonth, startday)
            enddate = startdate
        except ValueError:
            return None

    elif monthname_date:
        day = int(monthname_date.group(2))
        month = months_dict[monthname_date.group(1)]
        year = int(monthname_date.group(3))
        try:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        except ValueError:
            return None

    elif year_range:
        startyear = int(year_range.group(1))
        endyear = int(year_range.group(2))
        if int(endyear / 100) == 0:
            # endyear is only 2-digit: add the first two digits of startyear
            endyear = int(startyear / 100) * 100 + endyear

    elif year_only:
        startyear = int(year_only.group(0))
        endyear = startyear

    if startdate and enddate:
        return f"GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}"
    elif startyear and endyear:
        return f"GREGORIAN:CE:{startyear}:CE:{endyear}"
    else:
        return None


def prepare_value(
    value: Union[PropertyElement, str, int, float, bool, Iterable[Union[PropertyElement, str, int, float, bool]]]
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
    Start building your XML document by creating the root element <knora>.

    Args:
        shortcode: The shortcode of this project as defined in the JSON project file
        default ontology: one of the ontologies of the JSON project file

    Returns:
        The root element <knora>.

    Examples:
        >>> root = make_root(shortcode=shortcode, default_ontology=default_ontology)
        >>> root = append_permissions(root)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#the-root-element-knora
    """
    schema_url = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd"
    schema_location_key = str(etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"))
    schema_location_value = f"https://dasch.swiss/schema {schema_url}"
    root = etree.Element(
        "{%s}knora" % xml_namespace_map[None],
        attrib={
            schema_location_key: schema_location_value,
            "shortcode": shortcode,
            "default-ontology": default_ontology,
        },
        nsmap=xml_namespace_map,
    )
    return root


def append_permissions(root_element: etree._Element) -> etree._Element:
    """
    After having created a root element, call this method to append the four permissions "res-default",
    "res-restricted", "prop-default", and "prop-restricted" to it. These four permissions are a good basis to
    start with, but remember that they can be adapted, and that other permissions can be defined instead of these.

    Args:
        root_element: The XML root element <knora> created by make_root()

    Returns:
        The root element with the four permission blocks appended

    Examples:
        >>> root = make_root(shortcode=shortcode, default_ontology=default_ontology)
        >>> root = append_permissions(root)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-permissions-with-permissions-elements
    """

    PERMISSIONS = E.permissions
    ALLOW = E.allow
    # lxml.builder.E is a more sophisticated element factory than etree.Element.
    # E.tag is equivalent to E("tag") and results in <tag>

    res_default = etree.Element("{%s}permissions" % xml_namespace_map[None], id="res-default")
    res_default.append(ALLOW("V", group="UnknownUser"))
    res_default.append(ALLOW("V", group="KnownUser"))
    res_default.append(ALLOW("D", group="ProjectMember"))
    res_default.append(ALLOW("CR", group="ProjectAdmin"))
    res_default.append(ALLOW("CR", group="Creator"))
    root_element.append(res_default)

    res_restricted = PERMISSIONS(id="res-restricted")
    res_restricted.append(ALLOW("M", group="ProjectMember"))
    res_restricted.append(ALLOW("CR", group="ProjectAdmin"))
    res_restricted.append(ALLOW("CR", group="Creator"))
    root_element.append(res_restricted)

    prop_default = PERMISSIONS(id="prop-default")
    prop_default.append(ALLOW("V", group="UnknownUser"))
    prop_default.append(ALLOW("V", group="KnownUser"))
    prop_default.append(ALLOW("D", group="ProjectMember"))
    prop_default.append(ALLOW("CR", group="ProjectAdmin"))
    prop_default.append(ALLOW("CR", group="Creator"))
    root_element.append(prop_default)

    prop_restricted = PERMISSIONS(id="prop-restricted")
    prop_restricted.append(ALLOW("M", group="ProjectMember"))
    prop_restricted.append(ALLOW("CR", group="ProjectAdmin"))
    prop_restricted.append(ALLOW("CR", group="Creator"))
    root_element.append(prop_restricted)

    return root_element


def make_resource(
    label: str,
    restype: str,
    id: str,  # pylint: disable=redefined-builtin
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty resource element, with the attributes as specified by the arguments

    Args:
        The arguments correspond to the attributes of the <resource> element.

    Returns:
        The resource element, without any children, but with the attributes
        ``<resource label=label restype=restype id=id permissions=permissions ark=ark iri=iri></resource>``

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Examples:
        >>> resource = make_resource(...)
        >>> resource.append(make_text_prop(...))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-resources-with-the-resource-element
    """
    if not check_notna(label):
        warnings.warn(f"WARNING: Your resource's label looks suspicious (resource with id '{id}' and label '{label}'")
    if not check_notna(id):
        warnings.warn(f"WARNING: Your resource's id looks suspicious (resource with id '{id}' and label '{label}'")
    kwargs = {"label": label, "restype": restype, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(
            f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
            stacklevel=2,
        )
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The resource '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    resource_ = etree.Element("{%s}resource" % xml_namespace_map[None], **kwargs)  # type: ignore[arg-type]
    return resource_


def make_bitstream_prop(
    path: Union[str, os.PathLike[Any]],
    permissions: str = "prop-default",
    calling_resource: str = "",
) -> etree._Element:
    """
    Creates a bitstream element that points to "path".

    Args:
        path: path to a valid file that will be uploaded
        permissions: permissions string
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        Warning: if the path doesn't point to an existing file

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = make_resource(...)
        >>> resource.append(make_bitstream_prop("data/images/tree.jpg"))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#bitstream
    """

    if not os.path.isfile(path):
        warnings.warn(
            f"Failed validation in bitstream tag of resource '{calling_resource}': "
            f"The following path doesn't point to a file: {path}",
            stacklevel=2,
        )
    prop_ = etree.Element(
        "{%s}bitstream" % xml_namespace_map[None],
        permissions=permissions,
        nsmap=xml_namespace_map,
    )
    prop_.text = str(path)
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
    Make a <boolean-prop> from a boolean value. The value can be provided directly or inside a PropertyElement. The
    following formats are supported:
     - true: (True, "true", "True", "1", 1, "yes", "Yes")
     - false: (False, "false", "False", "0", 0, "no", "No")

    Unless provided as PropertyElement, the permissions of the value default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: a boolean value as str/bool/int, or as str/bool/int inside a PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: if the value is not a valid boolean

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_boolean_prop(":testproperty", "no")
                <boolean-prop name=":testproperty">
                    <boolean permissions="prop-default">false</boolean>
                </boolean-prop>
        >>> make_boolean_prop(":testproperty", PropertyElement("1", permissions="prop-restricted", comment="example"))
                <boolean-prop name=":testproperty">
                    <boolean permissions="prop-restricted" comment="example">true</boolean>
                </boolean-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#boolean-prop
    """

    # validate input
    if isinstance(value, PropertyElement):
        value_new = dataclasses.replace(value, value=_format_bool(value.value, name, calling_resource))
    elif isinstance(value, (str, bool, int)):
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
    Make a <color-prop> from one or more colors. The color(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP color(s), as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid color

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_color_prop(":testproperty", "#00ff66")
                <color-prop name=":testproperty">
                    <color permissions="prop-default">#00ff66</color>
                </color-prop>
        >>> make_color_prop(":testproperty", PropertyElement("#00ff66", permissions="prop-restricted", comment="example"))
                <color-prop name=":testproperty">
                    <color permissions="prop-restricted" comment="example">#00ff66</color>
                </color-prop>
        >>> make_color_prop(":testproperty", ["#00ff66", "#000000"])
                <color-prop name=":testproperty">
                    <color permissions="prop-default">#00ff66</color>
                    <color permissions="prop-default">#000000</color>
                </color-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#color-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^#[0-9a-f]{6}$", str(val.value).strip(), flags=re.IGNORECASE):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid color."
            )

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
    Make a <date-prop> from one or more dates/date ranges. The date(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP dates, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid DSP date

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_date_prop(":testproperty", "GREGORIAN:CE:2014-01-31")
                <date-prop name=":testproperty">
                    <date permissions="prop-default">GREGORIAN:CE:2014-01-31</date>
                </date-prop>
        >>> make_date_prop(":testproperty", PropertyElement("GREGORIAN:CE:2014-01-31", permissions="prop-restricted", comment="example"))
                <date-prop name=":testproperty">
                    <date permissions="prop-restricted" comment="example">
                        GREGORIAN:CE:2014-01-31
                    </date>
                </date-prop>
        >>> make_date_prop(":testproperty", ["GREGORIAN:CE:1930-09-02:CE:1930-09-03", "GREGORIAN:CE:1930-09-02:CE:1930-09-03"])
                <date-prop name=":testproperty">
                    <date permissions="prop-default">
                        GREGORIAN:CE:1930-09-02:CE:1930-09-03
                    </date>
                    <date permissions="prop-default">
                        GREGORIAN:CE:1930-09-02:CE:1930-09-03
                    </date>
                </date-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    validation_regex = (
        r"^(GREGORIAN:|JULIAN:)?(CE:|BCE:)?"
        + r"(\d{4})(-\d{1,2})?(-\d{1,2})?"
        + r"((:CE|:BCE)?(:\d{4})(-\d{1,2})?(-\d{1,2})?)?$"
    )
    for val in values:
        if not re.search(validation_regex, str(val.value).strip()):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid DSP date."
            )

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
    Make a <decimal-prop> from one or more decimal numbers. The decimal(s) can be provided as string, float, or as
    PropertyElement with a string/float inside. If provided as string/float, the permissions default to
    "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more decimal numbers, as string/float/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid decimal number

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_decimal_prop(":testproperty", "3.14159")
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-default">3.14159</decimal>
                </decimal-prop>
        >>> make_decimal_prop(":testproperty", PropertyElement("3.14159", permissions="prop-restricted", comment="example"))
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-restricted" comment="example">3.14159</decimal>
                </decimal-prop>
        >>> make_decimal_prop(":testproperty", ["3.14159", "2.718"])
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-default">3.14159</decimal>
                    <decimal permissions="prop-default">2.718</decimal>
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
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid decimal number."
            ) from None

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
        value_.text = str(float(val.value))
        prop_.append(value_)

    return prop_


def make_geometry_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a <geometry-prop> from one or more areas of an image. The area(s) can be provided as JSON-string or as
    PropertyElement with the JSON-string inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more JSON geometry objects, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid JSON geometry object

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_geometry_prop(":testproperty", json_string)
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-default">{JSON}</geometry>
                </geometry-prop>
        >>> make_geometry_prop(":testproperty", PropertyElement(json_string, permissions="prop-restricted", comment="example"))
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-restricted" comment="example">{JSON}</geometry>
                </geometry-prop>
        >>> make_geometry_prop(":testproperty", [json_string1, json_string2])
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-default">{JSON}</geometry>
                    <geometry permissions="prop-default">{JSON}</geometry>
                </geometry-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geometry-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            value_as_dict = json.loads(str(val.value))
            assert value_as_dict["type"] in ["rectangle", "circle", "polygon"]
            assert isinstance(value_as_dict["points"], list)
        except (json.JSONDecodeError, TypeError, IndexError, KeyError, AssertionError):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid JSON geometry object."
            ) from None

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
    Make a <geoname-prop> from one or more geonames.org IDs. The ID(s) can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more geonames.org IDs, as str/int/PropertyElement, or as iterable of str/int/PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid geonames.org identifier

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_geoname_prop(":testproperty", "2761369")
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-default">2761369</geoname>
                </geoname-prop>
        >>> make_geoname_prop(":testproperty", PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-restricted" comment="example">2761369</geoname>
                </geoname-prop>
        >>> make_geoname_prop(":testproperty", ["2761369", "1010101"])
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-default">2761369</geoname>
                    <geoname permissions="prop-default">1010101</geoname>
                </geoname-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#geoname-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^[0-9]+$", str(val.value)):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a geonames.org identifier."
            )

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
    Make a <integer-prop> from one or more integers. The integers can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more integers, as string/int/PropertyElement, or as iterable of strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid integer

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_integer_prop(":testproperty", "2761369")
                <integer-prop name=":testproperty">
                    <integer permissions="prop-default">2761369</integer>
                </integer-prop>
        >>> make_integer_prop(":testproperty", PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <integer-prop name=":testproperty">
                    <integer permissions="prop-restricted" comment="example">2761369</integer>
                </integer-prop>
        >>> make_integer_prop(":testproperty", ["2761369", "1010101"])
                <integer-prop name=":testproperty">
                    <integer permissions="prop-default">2761369</integer>
                    <integer permissions="prop-default">1010101</integer>
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
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid integer."
            ) from None

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
        value_.text = str(int(val.value))
        prop_.append(value_)

    return prop_


def make_interval_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a <interval-prop> from one or more DSP intervals. The interval(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP intervals, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the value is not a valid DSP interval

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_interval_prop(":testproperty", "61:3600")
                <interval-prop name=":testproperty">
                    <interval permissions="prop-default">61:3600</interval>
                </interval-prop>
        >>> make_interval_prop(":testproperty", PropertyElement("61:3600", permissions="prop-restricted", comment="example"))
                <interval-prop name=":testproperty">
                    <interval permissions="prop-restricted" comment="example">61:3600</interval>
                </interval-prop>
        >>> make_interval_prop(":testproperty", ["61:3600", "60.5:120.5"])
                <interval-prop name=":testproperty">
                    <interval permissions="prop-default">61:3600</interval>
                    <interval permissions="prop-default">60.5:120.5</interval>
                </interval-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#interval-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.match(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)):([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))", str(val.value)):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid DSP interval."
            )

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}interval-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if val.comment and check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}interval" % xml_namespace_map[None],
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
    Make a <list-prop> from one or more list nodes. The name(s) of the list node(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    Args:
        list_name: the name of the list as defined in the onto
        name: the name of this property as defined in the onto
        value: one or more node names, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the name of one of the list nodes is not a valid string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_list_prop("mylist", ":testproperty", "first_node")
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-default">first_node</list>
                </list-prop>
        >>> make_list_prop("mylist", ":testproperty", PropertyElement("first_node", permissions="prop-restricted", comment="example"))
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-restricted" comment="example">first_node</list>
                </list-prop>
        >>> make_list_prop("mylist", ":testproperty", ["first_node", "second_node"])
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-default">first_node</list>
                    <list permissions="prop-default">second_node</list>
                </list-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#list-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid name of a list node."
            )

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
    Make a <resptr-prop> from one or more IDs of other resources. The ID(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more resource identifiers, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If the ID of one of the target resources is not a valid string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_resptr_prop(":testproperty", "resource_1")
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-default">resource_1</resptr>
                </resptr-prop>
        >>> make_resptr_prop(":testproperty", PropertyElement("resource_1", permissions="prop-restricted", comment="example"))
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-restricted" comment="example">resource_1</resptr>
                </resptr-prop>
        >>> make_resptr_prop(":testproperty", ["resource_1", "resource_2"])
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-default">resource_1</resptr>
                    <resptr permissions="prop-default">resource_2</resptr>
                </resptr-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#resptr-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(
                f"Validation Error in resource '{calling_resource}', property '{name}': "
                f"The following doesn't seem to be a valid ID of a target resource: '{val.value}'"
            )

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
    Make a <text-prop> from one or more strings. The string(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the encoding defaults to utf8, and the permissions to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more strings, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: if one of the values is not a valid string,
            or if the XML tags in a richtext property (encoding=xml) are not well-formed
        Warning: if one of the values doesn't look like a reasonable string
            (e.g. "<NA>" is a valid string, but probably not intended)

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">first text</text>
                </text-prop>
        >>> make_text_prop(":testproperty", PropertyElement("first text", permissions="prop-restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">first text</text>
                </text-prop>
        >>> make_text_prop(":testproperty", ["first text", "second text"])
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">first text</text>
                    <text encoding="utf8" permissions="prop-default">second text</text>
                </text-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#text-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or len(val.value) < 1:
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid string."
            )
        if not check_notna(val.value):
            warnings.warn(
                f"Warning for resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is probably not a usable string.",
                stacklevel=2,
            )

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}text-prop" % xml_namespace_map[None],
        name=name,
        nsmap=xml_namespace_map,
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment  # type: ignore
        if check_notna(val.encoding):
            kwargs["encoding"] = val.encoding  # type: ignore
        else:
            kwargs["encoding"] = "utf8"
        value_ = etree.Element(
            "{%s}text" % xml_namespace_map[None],
            **kwargs,  # type: ignore
            nsmap=xml_namespace_map,
        )
        if kwargs["encoding"] == "utf8":
            # write the text into the tag, without validation
            value_.text = str(val.value)
        else:
            # enforce that the text is well-formed XML: serialize tag ...
            content = etree.tostring(value_, encoding="unicode")
            # ... insert text at the very end of the string, and add ending tag to the previously single <text/> tag ...
            content = re.sub(r"/>$", f">{val.value}</text>", content)
            # ... try to parse it again
            try:
                value_ = etree.fromstring(content)
            except etree.XMLSyntaxError:
                raise BaseError(
                    "The XML tags contained in a richtext property (encoding=xml) must be well-formed. "
                    "The special characters <, > and & are only allowed to construct a tag."
                    f"The error occurred in resource {calling_resource}, property {name}"
                ) from None
        prop_.append(value_)

    return prop_


def make_time_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = "",
) -> etree._Element:
    """
    Make a <time-prop> from one or more datetime values of the form "2009-10-10T12:00:00-05:00". The time(s) can be
    provided as string or as PropertyElement with a string inside. If provided as string, the permissions default to
    "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP times, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If one of the values is not a valid DSP time string

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_time_prop(":testproperty", "2009-10-10T12:00:00-05:00")
                <time-prop name=":testproperty">
                    <time permissions="prop-default">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> make_time_prop(":testproperty", PropertyElement("2009-10-10T12:00:00-05:00", permissions="prop-restricted", comment="example"))
                <time-prop name=":testproperty">
                    <time permissions="prop-restricted" comment="example">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> make_time_prop(":testproperty", ["2009-10-10T12:00:00-05:00", "1901-01-01T01:00:00-00:00"])
                <time-prop name=":testproperty">
                    <time permissions="prop-default">
                        2009-10-10T12:00:00-05:00
                    </time>
                    <time permissions="prop-default">
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
        if not re.search(validation_regex, str(val.value)):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid DSP time."
            )

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
    Make an <uri-prop> from one or more URIs. The URI(s) can be provided as string or as PropertyElement with a string
    inside. If provided as string, the permissions default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: one or more URIs, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Raises:
        BaseError: If one of the values is not a valid URI

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_uri_prop(":testproperty", "www.test.com")
                <uri-prop name=":testproperty">
                    <uri permissions="prop-default">www.test.com</uri>
                </uri-prop>
        >>> make_uri_prop(":testproperty", PropertyElement("www.test.com", permissions="prop-restricted", comment="example"))
                <uri-prop name=":testproperty">
                    <uri permissions="prop-restricted" comment="example">www.test.com</uri>
                </uri-prop>
        >>> make_uri_prop(":testproperty", ["www.1.com", "www.2.com"])
                <uri-prop name=":testproperty">
                    <uri permissions="prop-default">www.1.com</uri>
                    <uri permissions="prop-default">www.2.com</uri>
                </uri-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#uri-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            UriValue(str(val.value))
        except BaseError:
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid URI."
            ) from None

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


def make_region(
    label: str,
    id: str,  # pylint: disable=redefined-builtin
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty region element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <region> element.

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Returns:
        The region element, without any children, but with the attributes:
        <region label=label id=id permissions=permissions ark=ark iri=iri></region>

    Examples:
        >>> region = make_region("label", "id")
        >>> region.append(make_text_prop("hasComment", "This is a comment"))
        >>> region.append(make_color_prop("hasColor", "#5d1f1e"))
        >>> region.append(make_resptr_prop("isRegionOf", "image_0"))
        >>> region.append(make_geometry_prop("hasGeometry", "{...}"))
        >>> root.append(region)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#region
    """

    kwargs = {"label": label, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(
            f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
            stacklevel=2,
        )
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The region '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    region_ = etree.Element(
        "{%s}region" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )
    return region_


def make_annotation(
    label: str,
    id: str,  # pylint: disable=redefined-builtin
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty annotation element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <annotation> element.

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Returns:
        The annotation element, without any children, but with the attributes:
        <annotation label=label id=id permissions=permissions ark=ark iri=iri></annotation>

    Examples:
        >>> annotation = make_annotation("label", "id")
        >>> annotation.append(make_text_prop("hasComment", "This is a comment"))
        >>> annotation.append(make_resptr_prop("isAnnotationOf", "resource_0"))
        >>> root.append(annotation)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#annotation
    """

    kwargs = {"label": label, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(
            f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
            stacklevel=2,
        )
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The annotation '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    annotation_ = etree.Element(
        "{%s}annotation" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )
    return annotation_


def make_link(
    label: str,
    id: str,  # pylint: disable=redefined-builtin
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None,
) -> etree._Element:
    """
    Creates an empty link element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <link> element.

    Raises:
        Warning: if both an ARK and an IRI are provided
        BaseError: if the creation date is invalid

    Returns:
        The link element, without any children, but with the attributes:
        <link label=label id=id permissions=permissions ark=ark iri=iri></link>

    Examples:
        >>> link = make_link("label", "id")
        >>> link.append(make_text_prop("hasComment", "This is a comment"))
        >>> link.append(make_resptr_prop("hasLinkTo", ["resource_0", "resource_1"]))
        >>> root.append(link)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#link
    """

    kwargs = {"label": label, "id": id, "permissions": permissions, "nsmap": xml_namespace_map}
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(
            f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
            stacklevel=2,
        )
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(
                f"The link '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. "
                f"Did you perhaps forget the timezone?"
            ) from None
        kwargs["creation_date"] = creation_date

    link_ = etree.Element(
        "{%s}link" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )
    return link_


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
    excel_values_new = list()
    for val in excel_values:
        if isinstance(val, str):
            excel_values_new.extend([x.strip() for x in val.split(sep) if x])

    # read the list of the JSON project (works also for nested lists)
    with open(path_to_json, encoding="utf-8") as f:
        json_file = json.load(f)
    json_subset = list()
    for elem in json_file["project"]["lists"]:
        if elem["name"] == list_name:
            json_subset = elem["nodes"]
    json_values = set(_nested_dict_values_iterator(json_subset))

    # build dictionary with the mapping, based on string similarity
    res = dict()
    for excel_value in excel_values_new:
        excel_value_corrected = corrections.get(excel_value, excel_value)
        excel_value_simpl = simplify_name(excel_value_corrected)  # increase match probability by removing illegal chars
        matches: list[str] = difflib.get_close_matches(
            word=excel_value_simpl,
            possibilities=json_values,
            n=1,
            cutoff=0.6,
        )
        if matches:
            res[excel_value] = matches[0]
            res[excel_value.lower()] = matches[0]
        else:
            warnings.warn(
                f"Did not find a close match to the excel list entry '{excel_value}' "
                f"among the values in the JSON project list '{list_name}'",
                stacklevel=2,
            )

    return res


def _nested_dict_values_iterator(dicts: list[dict[str, Any]]) -> Iterable[str]:
    """
    This function accepts a list of nested dictionaries as argument
    and iterates over all values.
    It yields the values iteratively.
    """
    # Credits: https://thispointer.com/python-iterate-loop-over-all-nested-dictionary-values/
    for _dict in dicts:
        if "nodes" in _dict:
            for value in _nested_dict_values_iterator(_dict["nodes"]):
                yield value
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
    json_subset = list()
    for numbered_json_obj in json_file["project"]["lists"]:
        if numbered_json_obj["name"] == list_name:
            json_subset.append(numbered_json_obj)
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
    returns (label, name) pairs of JSON project list entries
    """
    for node in json_subset:
        # node is the json object containing the entire json-list
        if "nodes" in node:
            # "nodes" is the json sub-object containing the entries of the json-list
            for value in _name_label_mapper_iterator(node["nodes"], language_label):
                yield value
                # "value" is a (label, name) pair of a single list entry
        if "name" in node:
            yield (node["labels"][language_label], node["name"])
            # the actual values of the name and the label


def write_xml(
    root: etree._Element,
    filepath: str,
) -> None:
    """
    Write the finished XML to a file

    Args:
        root: etree Element with the entire XML document
        filepath: where to save the file

    Raises:
        Warning: if the XML is not valid according to the schema

    Returns:
        None
    """
    etree.indent(root, space="    ")
    xml_string = etree.tostring(
        root,
        encoding="unicode",
        pretty_print=True,
        doctype='<?xml version="1.0" encoding="UTF-8"?>',
    )
    xml_string = xml_string.replace(r"\'", "'")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_string)
    try:
        validate_xml_against_schema(input_file=filepath)
        print(f"The XML file was successfully saved to {filepath}")
    except BaseError as err:
        warnings.warn(
            f"The XML file was successfully saved to {filepath}, "
            f"but the following Schema validation error(s) occurred: {err.message}"
        )


def _read_cli_input_file(datafile: str) -> pd.DataFrame:
    """
    Parse the input file from the CLI (in either CSV or Excel format)

    Args:
        datafile: path to the input file

    Raises:
        BaseError: if the input file is neither .csv, .xls nor .xlsx

    Returns:
        a pandas DataFrame with the input data
    """
    if re.search(r"\.csv$", datafile):
        dataframe = pd.read_csv(
            filepath_or_buffer=datafile,
            encoding="utf_8_sig",  # utf_8_sig is the default encoding of Excel
            dtype="str",
            sep=None,
            engine="python",  # let the "python" engine detect the separator
        )
    elif re.search(r"(\.xls|\.xlsx)$", datafile):
        dataframe = pd.read_excel(io=datafile, dtype="str")
    else:
        raise BaseError(f"Cannot open file '{datafile}': Invalid extension. Allowed extensions: 'csv', 'xls', 'xlsx'")
    return dataframe


def _validate_and_prepare_cli_input_file(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Make sure that the required columns are present,
    replace NA-like cells by NA,
    remove empty columns, so that the max_num_of_props can be calculated without errors,
    and remove empty rows, to prevent them from being processed and raising an error.

    Args:
        dataframe: pandas dataframe with the input data

    Raises:
        BaseError: if one of the required columns is missing

    Returns:
        the prepared pandas DataFrame
    """
    # make sure that the required columns are present
    required_columns = ["id", "label", "restype", "permissions", "prop name", "prop type", "1_value"]
    if any(req not in dataframe for req in required_columns):
        raise BaseError(
            f"Some columns in your input file are missing. The following columns are required: {required_columns}"
        )

    # replace NA-like cells by NA
    dataframe = dataframe.applymap(
        lambda x: x if pd.notna(x) and regex.search(r"[\p{L}\d_!?\-]", str(x), flags=regex.U) else pd.NA
    )

    # remove empty columns/rows
    dataframe.dropna(axis="columns", how="all", inplace=True)
    dataframe.dropna(axis="index", how="all", inplace=True)

    return dataframe


def _convert_rows_to_xml(
    dataframe: pd.DataFrame,
    max_num_of_props: int,
) -> list[etree._Element]:
    """
    Iterate through the rows of the CSV/Excel input file,
    convert every row to either a XML resource or an XML property,
    and return a list of XML resources.

    Args:
        dataframe: pandas dataframe with the input data
        max_num_of_props: highest number of properties that a resource in this file has

    Raises:
        BaseError: if one of the rows is neither a resource-row nor a property-row,
            or if the file starts with a property-row

    Returns:
        a list of XML resources (with their respective properties)
    """
    resources: list[etree._Element] = []

    # to start, there is no previous resource
    resource: Optional[etree._Element] = None

    for index, row in dataframe.iterrows():
        row_number = int(str(index)) + 2
        # either the row is a resource-row or a property-row, but not both
        if check_notna(row["id"]) == check_notna(row["prop name"]):
            raise BaseError(
                f"Exactly 1 of the 2 columns 'id' and 'prop name' must be filled. "
                f"Excel row {row_number} has too many/too less entries:\n"
                f"id:        '{row['id']}'\n"
                f"prop name: '{row['prop name']}'"
            )

        # this is a resource-row
        elif check_notna(row["id"]):
            # the previous resource is finished, a new resource begins: append the previous to the resulting list
            # in all cases (except for the very first iteration), a previous resource exists
            if resource is not None:
                resources.append(resource)
            resource = _convert_resource_row_to_xml(row_number=row_number, row=row)

        # this is a property-row
        else:
            assert check_notna(row["prop name"])
            if resource is None:
                raise BaseError(
                    "The first row of your Excel/CSV is invalid. The first row must define a resource, not a property."
                )
            prop = _convert_property_row_to_xml(
                row_number=row_number,
                row=row,
                max_num_of_props=max_num_of_props,
                resource_id=resource.attrib["id"],
            )
            resource.append(prop)

    # append the resource of the very last iteration of the for loop
    if resource is not None:
        resources.append(resource)

    return resources


def _append_bitstream_to_resource(
    resource: etree._Element,
    row: pd.Series,
    row_number: int,
) -> etree._Element:
    """
    Create a bitstream-prop element, and append it to the resource.
    If the file permissions are missing, try to deduce them from the resource permissions.

    Args:
        resource: the resource element to which the bitstream-prop element should be appended
        row: the row of the CSV/Excel file from where all information comes from
        row_number: row number of the CSV/Excel sheet

    Raises:
        BaseError: if the file permissions are missing and cannot be deduced from the resource permissions

    Returns:
        the resource element with the appended bitstream-prop element
    """
    file_permissions = row.get("file permissions")
    if not check_notna(file_permissions):
        resource_permissions = row.get("permissions")
        if resource_permissions == "res-default":
            file_permissions = "prop-default"
        elif resource_permissions == "res-restricted":
            file_permissions = "prop-restricted"
        else:
            raise BaseError(
                f"Missing file permissions for file "
                f"'{row['file']}' (Resource ID '{row['id']}', Excel row {row_number}). "
                f"An attempt to deduce them from the resource permissions failed."
            )
    resource.append(
        make_bitstream_prop(
            path=str(row["file"]),
            permissions=str(file_permissions),
            calling_resource=row["id"],
        )
    )
    return resource


def _convert_resource_row_to_xml(
    row_number: int,
    row: pd.Series,
) -> etree._Element:
    """
    Convert a resource-row to an XML resource element.
    First, check if the mandatory cells are present.
    Then, call the appropriate function, depending on the restype (Resource, LinkObj, Annotation, Region).

    Args:
        row_number: row number of the CSV/Excel sheet
        row: the pandas series representing the current row

    Raises:
        BaseError: if a mandatory cell is missing

    Returns:
        the resource element created from the row
    """
    # read and check the mandatory columns
    resource_id = row["id"]
    resource_label = row.get("label")
    if pd.isna([resource_label]):
        raise BaseError(f"Missing label for resource '{resource_id}' (Excel row {row_number})")
    if not check_notna(resource_label):
        warnings.warn(
            f"The label of resource '{resource_id}' looks suspicious: '{resource_label}' (Excel row {row_number})"
        )
    resource_restype = row.get("restype")
    if not check_notna(resource_restype):
        raise BaseError(f"Missing restype for resource '{resource_id}' (Excel row {row_number})")
    resource_permissions = row.get("permissions")
    if not check_notna(resource_permissions):
        raise BaseError(f"Missing permissions for resource '{resource_id}' (Excel row {row_number})")

    # construct the kwargs for the method call
    kwargs_resource = {"label": resource_label, "permissions": resource_permissions, "id": resource_id}
    if check_notna(row.get("ark")):
        kwargs_resource["ark"] = row["ark"]
    if check_notna(row.get("iri")):
        kwargs_resource["iri"] = row["iri"]
    if check_notna(row.get("ark")) and check_notna(row.get("iri")):
        warnings.warn(
            f"Both ARK and IRI were provided for resource '{resource_label}' ({resource_id}). "
            "The ARK will override the IRI."
        )
    if check_notna(row.get("created")):
        kwargs_resource["creation_date"] = row["created"]

    # call the appropriate method
    if resource_restype == "Region":
        resource = make_region(**kwargs_resource)
    elif resource_restype == "Annotation":
        resource = make_annotation(**kwargs_resource)
    elif resource_restype == "LinkObj":
        resource = make_link(**kwargs_resource)
    else:
        kwargs_resource["restype"] = resource_restype
        resource = make_resource(**kwargs_resource)
        if check_notna(row.get("file")):
            resource = _append_bitstream_to_resource(
                resource=resource,
                row=row,
                row_number=row_number,
            )

    return resource


def _get_prop_function(
    row: pd.Series,
    resource_id: str,
) -> Callable[..., etree._Element]:
    """
    Return the function that creates the appropriate property, depending on the proptype.

    Args:
        row: row of the CSV/Excel sheet that defines the property
        resource_id: resource ID of the resource to which the property belongs

    Raises:
        BaseError: if the proptype is invalid

    Returns:
        the function that creates the appropriate property
    """
    proptype_2_function: dict[str, Callable[..., etree._Element]] = {
        "bitstream": make_bitstream_prop,
        "boolean-prop": make_boolean_prop,
        "color-prop": make_color_prop,
        "date-prop": make_date_prop,
        "decimal-prop": make_decimal_prop,
        "geometry-prop": make_geometry_prop,
        "geoname-prop": make_geoname_prop,
        "integer-prop": make_integer_prop,
        "interval-prop": make_interval_prop,
        "list-prop": make_list_prop,
        "resptr-prop": make_resptr_prop,
        "text-prop": make_text_prop,
        "uri-prop": make_uri_prop,
    }
    if row.get("prop type") not in proptype_2_function:
        raise BaseError(f"Invalid prop type for property {row.get('prop name')} in resource {resource_id}")
    make_prop_function = proptype_2_function[row["prop type"]]
    return make_prop_function


def _convert_row_to_property_elements(
    row: pd.Series,
    max_num_of_props: int,
    row_number: int,
    resource_id: str,
) -> list[PropertyElement]:
    """
    Every property contains i elements,
    which are represented in the Excel as groups of columns named
    {i_value, i_encoding, i_permissions, i_comment}.
    Depending on the property type, some of these cells are empty.
    This method converts a row to a list of PropertyElement objects.

    Args:
        row: the pandas series representing the current row
        max_num_of_props: highest number of properties that a resource in this file has
        row_number: row number of the CSV/Excel sheet
        resource_id: id of resource to which this property belongs to

    Raises:
        BaseError: if a mandatory cell is missing, or if there are too many/too few values per property

    Returns:
        list of PropertyElement objects
    """
    property_elements: list[PropertyElement] = []
    for i in range(1, max_num_of_props + 1):
        value = row[f"{i}_value"]
        if pd.isna(value):
            # raise error if other cells of this property element are not empty
            # if all other cells are empty, continue with next property element
            other_cell_headers = [f"{i}_{x}" for x in ["encoding", "permissions", "comment"]]
            notna_cell_headers = [x for x in other_cell_headers if check_notna(row.get(x))]
            notna_cell_headers_str = ", ".join([f"'{x}'" for x in notna_cell_headers])
            if notna_cell_headers_str:
                raise BaseError(
                    f"Error in resource '{resource_id}': Excel row {row_number} has an entry "
                    f"in column(s) {notna_cell_headers_str}, but not in '{i}_value'. "
                    r"Please note that cell contents that don't meet the requirements of the regex [\p{L}\d_!?\-] "
                    "are considered inexistent."
                )
            continue

        # construct a PropertyElement from this property element
        kwargs_propelem = {"value": value, "permissions": str(row.get(f"{i}_permissions"))}
        if not check_notna(row.get(f"{i}_permissions")):
            raise BaseError(
                f"Resource '{resource_id}': "
                f"Missing permissions in column '{i}_permissions' of property '{row['prop name']}'"
            )
        if check_notna(row.get(f"{i}_comment")):
            kwargs_propelem["comment"] = str(row[f"{i}_comment"])
        if check_notna(row.get(f"{i}_encoding")):
            kwargs_propelem["encoding"] = str(row[f"{i}_encoding"])
        property_elements.append(PropertyElement(**kwargs_propelem))

    # validate the end result before returning it
    if len(property_elements) == 0:
        raise BaseError(
            f"At least one value per property is required, "
            f"but resource '{resource_id}' (Excel row {row_number}) doesn't contain any values."
        )
    if row.get("prop type") == "boolean-prop" and len(property_elements) != 1:
        raise BaseError(
            f"A <boolean-prop> can only have a single value, "
            f"but resource '{resource_id}' (Excel row {row_number}) contains more than one value."
        )

    return property_elements


def _convert_property_row_to_xml(
    row_number: int,
    row: pd.Series,
    max_num_of_props: int,
    resource_id: str,
) -> etree._Element:
    """
    Convert a property-row of the CSV/Excel sheet to an XML element.

    Args:
        row_number: row number of the CSV/Excel sheet
        row: the pandas series representing the current row
        max_num_of_props: highest number of properties that a resource in this file has
        resource_id: id of the resource to which the property will be appended

    Raises:
        BaseError: if there is inconsistent data in the row / if a validation fails

    Returns:
        the resource element with the appended property
    """
    # based on the property type, the right function has to be chosen
    make_prop_function = _get_prop_function(
        row=row,
        resource_id=resource_id,
    )

    # convert the row to a list of PropertyElement objects
    property_elements = _convert_row_to_property_elements(
        row=row,
        max_num_of_props=max_num_of_props,
        row_number=row_number,
        resource_id=resource_id,
    )

    # create the property
    prop = _create_property(
        make_prop_function=make_prop_function,
        row=row,
        property_elements=property_elements,
        resource_id=resource_id,
    )
    return prop


def _create_property(
    make_prop_function: Callable[..., etree._Element],
    row: pd.Series,
    property_elements: list[PropertyElement],
    resource_id: str,
) -> etree._Element:
    """
    Create a property based on the appropriate function and the property elements.

    Args:
        make_prop_function: the function to create the property
        row: the pandas series representing the current row of the Excel/CSV
        property_elements: the list of PropertyElement objects
        resource_id: id of resource to which this property belongs to

    Returns:
        the resource with the properties appended
    """
    kwargs_propfunc: dict[str, Union[str, PropertyElement, list[PropertyElement]]] = {
        "name": row["prop name"],
        "calling_resource": resource_id,
    }

    if row.get("prop type") == "boolean-prop":
        kwargs_propfunc["value"] = property_elements[0]
    else:
        kwargs_propfunc["value"] = property_elements

    if check_notna(row.get("prop list")):
        kwargs_propfunc["list_name"] = str(row["prop list"])

    prop = make_prop_function(**kwargs_propfunc)

    return prop


def excel2xml(
    datafile: str,
    shortcode: str,
    default_ontology: str,
) -> bool:
    """
    This is a method that is called from the command line.
    It isn't intended to be used in a Python script.
    It takes a tabular data source in CSV/XLS(X) format that is formatted according to the specifications,
    and transforms it into a DSP-conforming XML file
    that can be uploaded to a DSP server with the xmlupload command.
    The output file is saved in the same directory as the input file,
    with the name [default_ontology]-data.xml.

    Please note that this method doesn't do any data cleaning or data transformation tasks.
    The input and the output of this method are semantically exactly equivalent.

    Args:
        datafile: path to the data file (CSV or XLS(X))
        shortcode: shortcode of the project that this data belongs to
        default_ontology: name of the ontology that this data belongs to

    Raises:
        BaseError if something went wrong

    Returns:
        True if everything went well, False otherwise
    """
    # read and prepare the input file
    success = True
    dataframe = _read_cli_input_file(datafile)
    dataframe = _validate_and_prepare_cli_input_file(dataframe)
    last_column_title = str(list(dataframe)[-1])  # last column title, in the format "i_comment"
    max_num_of_props = int(last_column_title.split("_")[0])

    # create the XML root element
    root = make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = append_permissions(root)

    # parse the input file row by row
    resources = _convert_rows_to_xml(
        dataframe=dataframe,
        max_num_of_props=max_num_of_props,
    )
    for resource in resources:
        root.append(resource)

    # write file
    with warnings.catch_warnings(record=True) as w:
        write_xml(root, f"{default_ontology}-data.xml")
        if len(w) > 0:
            success = False
    print(f"XML file successfully created at {default_ontology}-data.xml")

    return success
