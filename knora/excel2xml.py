import dataclasses
import datetime
import difflib
import json
import os
import re
import uuid
import warnings
from operator import xor
from typing import Any, Iterable, Optional, Union

import pandas as pd
import regex
from lxml import etree
from lxml.builder import E

from knora.dsplib.models.helpers import BaseError, DateTimeStamp
from knora.dsplib.models.propertyelement import PropertyElement
from knora.dsplib.models.value import UriValue
from knora.dsplib.utils.shared import simplify_name, check_notna, validate_xml_against_schema

xml_namespace_map = {
    None: "https://dasch.swiss/schema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}


def make_xsd_id_compatible(string: str) -> str:
    """
    Make a string compatible with the constraints of xsd:ID, so that it can be used as "id" attribute of a <resource>
    tag. An xsd:ID must not contain special characters, and it must be unique in the document.

    This method replaces the illegal characters by "_" and appends a random component to the string to make it unique.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``), underscore, !, ?, or number,
    but must not be "None", "<NA>", "N/A", or "-". Otherwise, a BaseError will be raised.

    Args:
        string: input string

    Returns:
        an xsd:ID based on the input string
    """

    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be transformed to an xsd:ID")

    # if start of string is neither letter nor underscore, add an underscore
    res = re.sub(r"^(?=[^A-Za-z_])", "_", string)

    # add uuid
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"

    # replace all illegal characters by underscore
    res = re.sub(r"[^\d\w_\-.]", "_", res)

    return res


def _derandomize_xsd_id(string: str, multiple_occurrences: bool = False) -> str:
    """
    In some contexts, the random component of the output of make_xsd_id_compatible() is a hindrance, especially for
    testing. This method removes the random part, but leaves the other modifications introduced by
    make_xsd_id_compatible() in place. This method's behaviour is defined by the example in the "Examples" section.

    Args:
        string: the output of make_xsd_id_compatible()
        multiple_occurrences: If true, string can be an entire XML document, and all occurrences will be removed

    Returns:
        the derandomized string

    Examples:
        >>> id_1 = make_xsd_id_compatible("Hello!")
        >>> id_2 = make_xsd_id_compatible("Hello!")
        >>> assert _derandomize_xsd_id(id_1) == _derandomize_xsd_id(id_2)
    """
    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be derandomized.")

    uuid4_regex = r"[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
    if multiple_occurrences:
        return re.subn(uuid4_regex, "", string, flags=re.IGNORECASE)[0]
    else:
        return re.sub(uuid4_regex, "", string, re.IGNORECASE)


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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#date-prop
    """

    # sanitize input, just in case that the method was called on an empty or N/A cell
    if not check_notna(string):
        return None
    string = str(string)

    monthes_dict = {
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
    iso_date = re.search(fr"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}", string)
    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range = re.search(fr"{lookbehind}{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex}?)? ?(?:-|:|to) ?"
                               fr"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex}{lookahead}", string)
    # template: 1.4.2021 | 5/11/2021
    eur_date = re.search(fr"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex}{lookahead}", string)
    # template: March 9, 1908 | March5,1908 | May 11, 1906
    monthname_date = re.search(
        fr"{lookbehind}(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept|"
        fr"October|Oct|November|Nov|December|Dec) ?{day_regex}, ?{year_regex}{lookahead}", string)
    # template: 1849/50 | 1849-50 | 1849/1850
    year_range = re.search(lookbehind + year_regex + r"[/-](\d{2}|\d{4})" +lookahead, string)
    # template: 1907
    year_only = re.search(fr"{lookbehind}{year_regex}{lookahead}", string)


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
        month = monthes_dict[monthname_date.group(1)]
        year = int(monthname_date.group(3))
        try:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        except ValueError:
            return None

    elif year_range:
        startyear = int(year_range.group(1))
        endyear = int(year_range.group(2))
        if int(endyear/100) == 0:
            # endyear is only 2-digit: add the first two digits of startyear
            endyear = int(startyear/100) * 100 + endyear

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


def make_root(shortcode: str, default_ontology: str) -> etree._Element:
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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#the-root-element-knora
    """

    root = etree.Element(
        _tag="{%s}knora" % (xml_namespace_map[None]),
        attrib={
            str(etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")):
                "https://dasch.swiss/schema " + \
                "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd",
            "shortcode": shortcode,
            "default-ontology": default_ontology
        },
        nsmap=xml_namespace_map
    )
    return root


def append_permissions(root_element: etree.Element) -> etree._Element:
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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#describing-permissions-with-permissions-elements
    """

    PERMISSIONS = E.permissions
    ALLOW = E.allow
    # lxml.builder.E is a more sophisticated element factory than etree.Element.
    # E.tag is equivalent to E("tag") and results in <tag>

    res_default = etree.Element("{%s}permissions" % (xml_namespace_map[None]), id="res-default")
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
    id: str,
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None
) -> etree._Element:
    """
    Creates an empty resource element, with the attributes as specified by the arguments

    Args:
        The arguments correspond to the attributes of the <resource> element.

    Returns:
        The resource element, without any children, but with the attributes
        ``<resource label=label restype=restype id=id permissions=permissions ark=ark iri=iri></resource>``

    Examples:
        >>> resource = make_resource(...)
        >>> resource.append(make_text_prop(...))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#describing-resources-with-the-resource-element
    """

    kwargs = {
        "label": label,
        "restype": restype,
        "id": id,
        "permissions": permissions,
        "nsmap": xml_namespace_map
    }
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
                      stacklevel=2)
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(f"The resource '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. Did "
                            f"you perhaps forget the timezone?")
        kwargs["creation_date"] = creation_date

    resource_ = etree.Element(
        "{%s}resource" % (xml_namespace_map[None]),
        **kwargs
    )
    return resource_


def make_bitstream_prop(
    path: str,
    permissions: str = "prop-default",
    calling_resource: str = ""
) -> etree._Element:
    """
    Creates a bitstream element that points to "path". If "path" doesn't point to a valid file, a warning will be
    printed to the console, but the script will continue.

    Args:
        path: path to a valid file that will be uploaded
        permissions: permissions string
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = make_resource(...)
        >>> resource.append(make_bitstream_prop("data/images/tree.jpg"))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#bitstream
    """

    if not os.path.isfile(path):
        warnings.warn(f"Failed validation in bitstream tag of resource '{calling_resource}': The following path "
                      f"doesn't point to a file: {path}",
                      stacklevel=2)
    prop_ = etree.Element("{%s}bitstream" % (xml_namespace_map[None]), permissions=permissions,
                          nsmap=xml_namespace_map)
    prop_.text = path
    return prop_


def _format_bool(unformatted: Union[bool, str, int], name: str, calling_resource: str) -> str:
    if isinstance(unformatted, str):
        unformatted = unformatted.lower()
    if unformatted in (False, "false", "0", 0, "no"):
        return "false"
    elif unformatted in (True, "true", "1", 1, "yes"):
        return "true"
    else:
        raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                        f"'{unformatted}' is not a valid boolean.")


def make_boolean_prop(
    name: str,
    value: Union[PropertyElement, str, int, bool],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <boolean-prop> from a boolean value. The value can be provided directly or inside a PropertyElement. The
    following formats are supported:
     - true: (True, "true", "True", "1", 1, "yes", "Yes")
     - false: (False, "false", "False", "0", 0, "no", "No")

    If the value is not a valid boolean, a BaseError will be raised.

    Unless provided as PropertyElement, the permissions of the value default to "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: a boolean value as str/bool/int, or as str/bool/int inside a PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#boolean-prop
    """

    # validate input
    if isinstance(value, PropertyElement):
        value_new = dataclasses.replace(value, value=_format_bool(value.value, name, calling_resource))
    elif isinstance(value, str) or isinstance(value, bool) or isinstance(value, int):
        value_new = PropertyElement(_format_bool(value, name, calling_resource))
    else:
        raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                        f"'{value}' is not a valid boolean.")

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}boolean-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    kwargs = {"permissions": value_new.permissions}
    if check_notna(value_new.comment):
        kwargs["comment"] = value_new.comment
    value_ = etree.Element(
        "{%s}boolean" % (xml_namespace_map[None]),
        **kwargs,
        nsmap=xml_namespace_map
    )
    value_.text = value_new.value
    prop_.append(value_)

    return prop_


def make_color_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <color-prop> from one or more colors. The color(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the permissions default to "prop-default".

    If the value is not a valid color, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP color(s), as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#color-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^#[0-9a-f]{6}$", str(val.value).strip(), flags=re.IGNORECASE):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid color.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}color-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}color" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value).strip()
        prop_.append(value_)

    return prop_


def make_date_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <date-prop> from one or more dates/date ranges. The date(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permissions default to "prop-default".

    If the value is not a valid DSP date, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP dates, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#date-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\d{4})(-\d{1,2})?(-\d{1,2})?"
                         r"((:CE|:BCE)?(:\d{4})(-\d{1,2})?(-\d{1,2})?)?$", str(val.value).strip()):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid DSP date.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}date-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}date" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value).strip()
        prop_.append(value_)

    return prop_


def make_decimal_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <decimal-prop> from one or more decimal numbers. The decimal(s) can be provided as string, float, or as
    PropertyElement with a string/float inside. If provided as string/float, the permissions default to
    "prop-default".

    If the value is not a valid decimal number, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more decimal numbers, as string/float/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#decimal-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            float(val.value)
        except ValueError:
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid decimal number.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}decimal-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}decimal" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(float(val.value))
        prop_.append(value_)

    return prop_


def make_geometry_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <geometry-prop> from one or more areas of an image. The area(s) can be provided as JSON-string or as
    PropertyElement with the JSON-string inside. If provided as string, the permissions default to "prop-default".

    If the value is not a valid JSON geometry object, a BaseError is raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more JSON geometry objects, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#geometry-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            value_as_dict = json.loads(val.value)
            assert value_as_dict["type"] in ["rectangle", "circle", "polygon"]
            assert isinstance(value_as_dict["points"], list)
        except (json.JSONDecodeError, TypeError, IndexError, KeyError, AssertionError):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid JSON geometry object.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}geometry-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}geometry" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value)
        prop_.append(value_)
    return prop_


def make_geoname_prop(
    name: str,
    value: Union[PropertyElement, str, int, Iterable[Union[PropertyElement, str, int]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <geoname-prop> from one or more geonames.org IDs. The ID(s) can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "prop-default".

    If the value is not a valid geonames.org identifier, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more geonames.org IDs, as string/int/PropertyElement, or as iterable of strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#geoname-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^[0-9]+$", str(val.value)):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a geonames.org identifier.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}geoname-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}geoname" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_integer_prop(
    name: str,
    value: Union[PropertyElement, str, int, Iterable[Union[PropertyElement, str, int]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <integer-prop> from one or more integers. The integers can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permissions default to
    "prop-default".

    If the value is not a valid integer, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more integers, as string/int/PropertyElement, or as iterable of strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#integer-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            int(val.value)
        except ValueError:
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid integer.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}integer-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}integer" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(int(val.value))
        prop_.append(value_)

    return prop_


def make_interval_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <interval-prop> from one or more DSP intervals. The interval(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    If the value is not a valid DSP interval, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP intervals, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#interval-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.match(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)):([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))", str(val.value)):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid DSP interval.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}interval-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}interval" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_list_prop(
    list_name: str,
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <list-prop> from one or more list nodes. The name(s) of the list node(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    If the name of one of the list nodes is not a valid string, a BaseError will be raised.

    Args:
        list_name: the name of the list as defined in the onto
        name: the name of this property as defined in the onto
        value: one or more node names, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#list-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid name of a list node.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}list-prop" % (xml_namespace_map[None]),
        list=list_name,
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}list" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_resptr_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <resptr-prop> from one or more IDs of other resources. The ID(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permissions default to "prop-default".

    If the ID of one of the target resources is not a valid string, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more resource identifiers, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#resptr-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(f"Validation Error in resource '{calling_resource}', property '{name}': "
                            f"The following doesn't seem to be a valid ID of a target resource: '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}resptr-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}resptr" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_text_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <text-prop> from one or more strings. The string(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the encoding defaults to utf8, and the permissions to "prop-default".

    If the value is not a valid string, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more strings, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#text-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not isinstance(val.value, str) or len(val.value) < 1:
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid string.")
        if not check_notna(val.value):
            warnings.warn(f"Warning for resource '{calling_resource}', property '{name}': "
                          f"'{val.value}' is probably not a usable string.", stacklevel=2)

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}text-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        if check_notna(val.encoding):
            kwargs["encoding"] = val.encoding
        else:
            kwargs["encoding"] = "utf8"
        value_ = etree.Element(
            "{%s}text" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_time_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make a <time-prop> from one or more datetime values of the form "2009-10-10T12:00:00-05:00". The time(s) can be
    provided as string or as PropertyElement with a string inside. If provided as string, the permissions default to
    "prop-default".

    If one of the values is not a valid DSP time string, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more DSP times, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#time-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        if not re.search(r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$", str(val.value)):
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid DSP time.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}time-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}time" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_uri_prop(
    name: str,
    value: Union[PropertyElement, str, Iterable[Union[PropertyElement, str]]],
    calling_resource: str = ""
) -> etree._Element:
    """
    Make an <uri-prop> from one or more URIs. The URI(s) can be provided as string or as PropertyElement with a string
    inside. If provided as string, the permissions default to "prop-default".

    If one of the values is not a valid URI, a BaseError will be raised.

    Args:
        name: the name of this property as defined in the onto
        value: one or more URIs, as string/PropertyElement, or as iterable of strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#uri-prop
    """

    # check the input: prepare a list with valid values
    values = prepare_value(value)

    # check value type
    for val in values:
        try:
            UriValue(str(val.value))
        except BaseError:
            raise BaseError(f"Failed validation in resource '{calling_resource}', property '{name}': "
                            f"'{val.value}' is not a valid URI.")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}uri-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}uri" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_region(
    label: str,
    id: str,
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None
) -> etree._Element:
    """
    Creates an empty region element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <region> element.

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

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#region
    """

    kwargs = {
        "label": label,
        "id": id,
        "permissions": permissions,
        "nsmap": xml_namespace_map
    }
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
                      stacklevel=2)
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(f"The region '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. Did "
                            f"you perhaps forget the timezone?")
        kwargs["creation_date"] = creation_date

    region_ = etree.Element(
        "{%s}region" % (xml_namespace_map[None]),
        **kwargs
    )
    return region_


def make_annotation(
    label: str,
    id: str,
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None
) -> etree._Element:
    """
    Creates an empty annotation element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <annotation> element.

    Returns:
        The annotation element, without any children, but with the attributes:
        <annotation label=label id=id permissions=permissions ark=ark iri=iri></annotation>

    Examples:
        >>> annotation = make_annotation("label", "id")
        >>> annotation.append(make_text_prop("hasComment", "This is a comment"))
        >>> annotation.append(make_resptr_prop("isAnnotationOf", "resource_0"))
        >>> root.append(annotation)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#annotation
    """

    kwargs = {
        "label": label,
        "id": id,
        "permissions": permissions,
        "nsmap": xml_namespace_map
    }
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
                      stacklevel=2)
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(f"The annotation '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. Did "
                            f"you perhaps forget the timezone?")
        kwargs["creation_date"] = creation_date

    annotation_ = etree.Element(
        "{%s}annotation" % (xml_namespace_map[None]),
        **kwargs
    )
    return annotation_


def make_link(
    label: str,
    id: str,
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None,
    creation_date: Optional[str] = None
) -> etree._Element:
    """
    Creates an empty link element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <link> element.

    Returns:
        The link element, without any children, but with the attributes:
        <link label=label id=id permissions=permissions ark=ark iri=iri></link>

    Examples:
        >>> link = make_link("label", "id")
        >>> link.append(make_text_prop("hasComment", "This is a comment"))
        >>> link.append(make_resptr_prop("hasLinkTo", ["resource_0", "resource_1"]))
        >>> root.append(link)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#link
    """

    kwargs = {
        "label": label,
        "id": id,
        "permissions": permissions,
        "nsmap": xml_namespace_map
    }
    if ark:
        kwargs["ark"] = ark
    if iri:
        kwargs["iri"] = iri
    if ark and iri:
        warnings.warn(f"Both ARK and IRI were provided for resource '{label}' ({id}). The ARK will override the IRI.",
                      stacklevel=2)
    if creation_date:
        try:
            DateTimeStamp(creation_date)
        except BaseError:
            raise BaseError(f"The link '{label}' (ID: {id}) has an invalid creation date '{creation_date}'. Did "
                            f"you perhaps forget the timezone?")
        kwargs["creation_date"] = creation_date

    link_ = etree.Element(
        "{%s}link" % (xml_namespace_map[None]),
        **kwargs
    )
    return link_


def create_json_excel_list_mapping(
    path_to_json: str,
    list_name: str,
    excel_values: Iterable[str],
    sep: str = '+"*ç%&/()=',
    corrections: Optional[dict[str, str]] = None
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

    Returns:
        dict of the form {excel_value: list_node_name}. Every excel_value is stripped, and also present in a lowercase form.

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
        >>> json_excel_list_mapping = {"Giraffeeh": "giraffe", "Girraffe": "giraffe", "Antiloupe": "antelope",
        >>>                            "giraffeeh": "giraffe", "girraffe": "giraffe", "antiloupe": "antelope"}
    """

    # avoid mutable default argument
    corrections = corrections or {}

    # split the values, if necessary
    excel_values_new = list()
    for val in excel_values:
        if isinstance(val, str):
            excel_values_new.extend([x.strip() for x in val.split(sep) if x])

    # read the list of the JSON project (works also for nested lists)
    with open(path_to_json) as f:
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
        excel_value_simpl = simplify_name(excel_value_corrected)  #increase match probability by removing illegal chars
        matches: list[str] = difflib.get_close_matches(
            word=excel_value_simpl,
            possibilities=json_values,
            n=1,
            cutoff=0.6
        )
        if matches:
            res[excel_value] = matches[0]
            res[excel_value.lower()] = matches[0]
        else:
            warnings.warn(f"Did not find a close match to the excel list entry '{excel_value}' among the values "
                          f"in the JSON project list '{list_name}'", stacklevel=2)

    return res


def _nested_dict_values_iterator(dicts: list[dict[str, Any]]) -> Iterable[str]:
    """ This function accepts a list of nested dictionaries as argument
        and iterates over all values. It yields the values iteratively.
        Credits: https://thispointer.com/python-iterate-loop-over-all-nested-dictionary-values/
    """

    for dict in dicts:
        if "nodes" in dict:
            for value in _nested_dict_values_iterator(dict["nodes"]):
                yield value
        if "name" in dict:
            yield dict["name"]


def create_json_list_mapping(
    path_to_json: str,
    list_name: str,
    language_label: str
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
    with open(path_to_json) as f:
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


def _name_label_mapper_iterator(json_subset: list[dict[str, Any]], language_label: str) -> Iterable[tuple[str, str]]:
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


def write_xml(root: etree.Element, filepath: str) -> None:
    """
    Write the finished XML to a file

    Args:
        root: etree Element with the entire XML document
        filepath: where to save the file

    Returns:
        None
    """
    etree.indent(root, space="    ")
    xml_string = etree.tostring(root, encoding="unicode", pretty_print=True)
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    xml_string = xml_string.replace("&lt;", "<")
    xml_string = xml_string.replace("&gt;", ">")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_string)
    try:
        validate_xml_against_schema(filepath)
        print(f"The XML file was successfully saved to {filepath}")
    except BaseError as err:
        warnings.warn(f"The XML file was successfully saved to {filepath}, but the following Schema validation "
                      f"error(s) occurred: {err.message}")


def excel2xml(datafile: str, shortcode: str, default_ontology: str) -> None:
    """
    This is a method that is called from the command line. It isn't intended to be used in a Python script. It takes a
    tabular data source in CSV/XLS(X) format that is formatted according to the specifications, and transforms it to DSP-
    conforming XML file that can be uploaded to a DSP server with the xmlupload command. The output file is saved in the
    same directory as the input file, with the name [default_ontology]-data.xml.

    Please note that this method doesn't do any data cleaning or data transformation tasks. The input and the output of
    this method are semantically exactly equivalent.

    Args:
        datafile: path to the data file (CSV or XLS(X))
        shortcode: shortcode of the project that this data belongs to
        default_ontology: name of the ontology that this data belongs to

    Returns:
        None
    """

    # general preparation
    # -------------------
    proptype_2_function = {
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
        "uri-prop": make_uri_prop
    }
    if re.search(r"\.csv$", datafile):
        # "utf_8_sig": an optional BOM at the start of the file will be skipped
        # let the "python" engine detect the separator
        main_df = pd.read_csv(datafile, encoding="utf_8_sig", dtype="str", sep=None, engine="python")
    elif re.search(r"(\.xls|\.xlsx)$", datafile):
        main_df = pd.read_excel(datafile, dtype="str")
    else:
        raise BaseError("The argument 'datafile' must have one of the extensions 'csv', 'xls', 'xlsx'")
    # replace NA-like cells by NA
    main_df = main_df.applymap(
        lambda x: x if pd.notna(x) and regex.search(r"[\p{L}\d_!?\-]", str(x), flags=regex.U) else pd.NA
    )
    # remove empty columns, so that the max_prop_count can be calculated without errors
    main_df.dropna(axis="columns", how="all", inplace=True)
    # remove empty rows, to prevent them from being processed and raising an error
    main_df.dropna(axis="index", how="all", inplace=True)
    max_prop_count = int(list(main_df)[-1].split("_")[0])
    root = make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = append_permissions(root)
    resource_id: str = ""

    # create all resources
    # --------------------
    for index, row in main_df.iterrows():

        # there are two cases: either the row is a resource-row or a property-row.
        if not xor(check_notna(row.get("id")), check_notna(row.get("prop name"))):
            raise BaseError(f"Exactly 1 of the 2 columns 'id' and 'prop name' must have an entry. Excel row no. "
                            f"{int(str(index)) + 2} has too many/too less entries:\n"
                            f"id:        '{row.get('id')}'\n"
                            f"prop name: '{row.get('prop name')}'")

        ########### case resource-row ###########
        if check_notna(row.get("id")):
            resource_id = row["id"]
            resource_permissions = row.get("permissions")
            if not check_notna(resource_permissions):
                raise BaseError(f"Missing permissions for resource {resource_id}")
            resource_label = row.get("label")
            if not check_notna(resource_label):
                raise BaseError(f"Missing label for resource {resource_id}")
            resource_restype = row.get("restype")
            if not check_notna(resource_restype):
                raise BaseError(f"Missing restype for resource {resource_id}")
            # previous resource is finished, now a new resource begins. in all cases (except for
            # the very first iteration), a previous resource exists. if it exists, append it to root.
            if "resource" in locals():
                root.append(resource)
            kwargs_resource = {
                "label": resource_label,
                "permissions": resource_permissions,
                "id": resource_id
            }
            if check_notna(row.get("ark")):
                kwargs_resource["ark"] = row["ark"]
            if check_notna(row.get("iri")):
                kwargs_resource["iri"] = row["iri"]
            if check_notna(row.get("created")):
                kwargs_resource["creation_date"] = row["created"]
            if resource_restype not in ["Annotation", "Region", "LinkObj"]:
                kwargs_resource["restype"] = resource_restype
                resource = make_resource(**kwargs_resource)
                if check_notna(row.get("file")):
                    file_permissions = row.get("file permissions")
                    if not check_notna(file_permissions):
                        if resource_permissions == "res-default":
                            file_permissions = "prop-default"
                        elif resource_permissions == "res-restricted":
                            file_permissions = "prop-restricted"
                        else:
                            raise BaseError(f"'file permissions' missing for file '{row['file']}' (Excel row "
                                            f"{int(str(index)) + 2}). An attempt to deduce them from the resource "
                                            f"permissions failed.")
                    resource.append(make_bitstream_prop(
                        path=str(row["file"]),
                        permissions=file_permissions,
                        calling_resource=resource_id
                    ))
            elif resource_restype == "Region":
                resource = make_region(**kwargs_resource)
            elif resource_restype == "Annotation":
                resource = make_annotation(**kwargs_resource)
            elif resource_restype == "LinkObj":
                resource = make_link(**kwargs_resource)

        ########### case property-row ###########
        else:  # check_notna(row["prop name"]):
            # based on the property type, the right function has to be chosen
            if row.get("prop type") not in proptype_2_function:
                raise BaseError(f"Invalid prop type for property {row.get('prop name')} in resource {resource_id}")
            make_prop_function = proptype_2_function[row["prop type"]]

            # every property contains i elements, which are represented in the Excel as groups of
            # columns named {i_value, i_encoding, i_res ref, i_permissions, i_comment}. Depending
            # on the property type, some of these items are NA.
            # Thus, prepare list of PropertyElement objects, with each PropertyElement containing only
            # the existing items.
            property_elements: list[PropertyElement] = []
            for i in range(1, max_prop_count + 1):
                value = row[f"{i}_value"]
                if pd.notna(value):
                    kwargs_propelem = {
                        "value": value,
                        "permissions": str(row.get(f"{i}_permissions"))
                    }
                    if not check_notna(row.get(f"{i}_permissions")):
                        raise BaseError(f"Missing permissions for value {value} of property {row['prop name']} "
                                        f"in resource {resource_id}")
                    if check_notna(row.get(f"{i}_comment")):
                        kwargs_propelem["comment"] = str(row[f"{i}_comment"])
                    if check_notna(row.get(f"{i}_encoding")):
                        kwargs_propelem["encoding"] = str(row[f"{i}_encoding"])

                    property_elements.append(PropertyElement(**kwargs_propelem))
                elif check_notna(str(row.get(f"{i}_permissions"))):
                    raise BaseError(f"Excel row {int(str(index)) + 2} has an entry in column {i}_permissions, but not "
                                    f"in {i}_value. Please note that cell contents that don't meet the requirements of "
                                    r"the regex [\p{L}\d_!?\-] are considered inexistent.")

            # validate property_elements
            if len(property_elements) == 0:
                raise BaseError(f"At least one value per property is required, but Excel row {int(str(index)) + 2}"
                                f"doesn't contain any values.")
            if make_prop_function == make_boolean_prop and len(property_elements) != 1:
                raise BaseError(f"A <boolean-prop> can only have a single value, but Excel row {int(str(index)) + 2} "
                                f"contains more than one values.")

            # create the property and append it to resource
            kwargs_propfunc: dict[str, Union[str, PropertyElement, list[PropertyElement]]] = {
                "name": row["prop name"],
                "calling_resource": resource_id
            }
            if make_prop_function == make_boolean_prop:
                kwargs_propfunc["value"] = property_elements[0]
            else:
                kwargs_propfunc["value"] = property_elements
            if check_notna(row.get("prop list")):
                kwargs_propfunc["list_name"] = str(row["prop list"])

            resource.append(make_prop_function(**kwargs_propfunc))

    # append the resource of the very last iteration of the for loop
    root.append(resource)

    # write file
    # ----------
    write_xml(root, f"{default_ontology}-data.xml")
    print(f"XML file successfully created at {default_ontology}-data.xml")
