import datetime
import json
import os
import re
import uuid
import warnings
import difflib
from operator import xor
import regex

import pandas as pd
from typing import Any, Iterable, Optional, Union
from lxml import etree
from lxml.builder import E
import dataclasses

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.excel_to_json_lists import simplify_name

##############################
# global variables and classes
##############################
xml_namespace_map = {
    None: "https://dasch.swiss/schema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}


@dataclasses.dataclass(frozen=True)
class PropertyElement:
    """
    A PropertyElement object carries more information about a property value than the value itself.
    The "value" is the value that could be passed to a method as plain string/int/float/bool. Use a PropertyElement
    instead to define more precisely what attributes your <text> tag (for example) will have.

    Args:
        value: This is the content that will be written between the <text></text> tags (for example)
        permissions: This is the permissions that your <text> tag (for example) will have
        comment: This is the comment that your <text> tag (for example) will have
        encoding: For <text> tags only. Can be "xml" or "utf8".

    Examples:
        See the difference between the first and the second example:

        >>> make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">
                        first text
                    </text>
                </text-prop>
        >>> make_text_prop(":testproperty", PropertyElement("first text", permissions="prop-restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">
                        first text
                    </text>
                </text-prop>
    """
    value: Union[str, int, float, bool]
    permissions: str = "prop-default"
    comment: Optional[str] = None
    encoding: Optional[str] = None

    def __post_init__(self) -> None:
        if not check_notna(self.value):
            raise BaseError(f"'{self.value}' is not a valid value for a PropertyElement")
        if self.encoding not in ["utf8", "xml", None]:
            raise BaseError(f"'{self.encoding}' is not a valid encoding for a PropertyElement")


###########
# functions
###########
def make_xsd_id_compatible(string: str) -> str:
    """
    Make a string compatible with the constraints of xsd:ID as defined in http://www.datypic.com/sc/xsd/t-xsd_ID.html.
    An xsd:ID cannot contain special characters, and it must be unique in the document.

    This method replaces the illegal characters by "_" and appends a random number to the string to make it unique.

    The string must contain at least one word-character (regex [A-Za-z0-9_]), but must not be "None", "<NA>", "N/A", or
    "-". In such cases, a BaseError is thrown.

    Args:
        string: string which to make the xsd:ID from

    Returns:
        an `xsd:ID` based on string
    """

    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The string {string} cannot be made an xsd:ID")

    # if start of string is neither letter nor underscore, add an underscore
    res = re.sub(r"^(?=[^A-Za-z_])", "_", string)

    # add uuid
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"

    # replace all illegal characters by underscore
    res = re.sub(r"[^\d\w_\-.]", "_", res)

    return res


def find_date_in_string(string: str, calling_resource: str = "") -> Optional[str]:
    """
    Checks if a string contains a date value (single date, or date range), and returns the first found date as
    DSP-formatted string. Returns None if no date was found.

    Notes:
        - Assumes Christian era (no BC dates) and Gregorian calendar.
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
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        DSP-formatted date string, or None

    Examples:
        >>> if find_date_in_string(row["Epoch"]):
        >>>     resource.append(make_date_prop(":hasDate", find_date_in_string(row["Epoch"]))

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#date-prop
    """

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
            warnings.warn(f"Date parsing error in resource {calling_resource}: '{iso_date.group(0)}' is not a valid "
                          f"date", stacklevel=2)
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
            warnings.warn(f"Date parsing error in resource {calling_resource}: '{eur_date_range.group(0)}' is not a "
                          f"valid date", stacklevel=2)
            return None

    elif eur_date:
        startday = int(eur_date.group(1))
        startmonth = int(eur_date.group(2))
        startyear = int(eur_date.group(3))
        try:
            startdate = datetime.date(startyear, startmonth, startday)
            enddate = startdate
        except ValueError:
            warnings.warn(f"Date parsing error in resource {calling_resource}: '{eur_date.group(0)}' is not a valid "
                          f"date", stacklevel=2)
            return None

    elif monthname_date:
        day = int(monthname_date.group(2))
        month = monthes_dict[monthname_date.group(1)]
        year = int(monthname_date.group(3))
        try:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        except ValueError:
            warnings.warn(f"Date parsing error in resource {calling_resource}: '{monthname_date.group(0)}' is not a "
                          f"valid date", stacklevel=2)
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


def check_notna(value: Optional[Any]) -> bool:
    """
    Check a value if it is usable in the context of data archiving. A value is considered usable if it is
     - a number (integer or float, but not np.nan)
     - a boolean
     - a string with at least one word-character (regex `[A-Za-z0-9_]`), but not "None", "<NA>", "N/A", or "-"
     - a PropertyElement whose "value" fulfills the above criteria

    Args:
        value: any object encountered when analysing data

    Returns:
        True if the value is usable, False if it is N/A or otherwise unusable
    """

    if isinstance(value, PropertyElement):
        value = value.value

    if any([
        isinstance(value, int),
        isinstance(value, float) and pd.notna(value),   # necessary because isinstance(np.nan, float)
        isinstance(value, bool)
    ]):
        return True
    elif isinstance(value, str):
        return all([
            regex.search(r"\p{L}|\d|_", value, flags=re.UNICODE),
            not bool(re.search(r"^(none|<NA>|-|n/a)$", value, flags=re.IGNORECASE))
        ])
    else:
        return False


def _check_and_prepare_values(
    value: Optional[Union[PropertyElement, str, int, float, bool]],
    values: Optional[Iterable[Union[PropertyElement, str, int, float, bool]]],
    name: str,
    calling_resource: str = ""
) -> list[PropertyElement]:
    """
    There is a variety of possibilities how to call a make_*_prop() method. Before such a method can do its job, the
    parameters need to be checked and prepared, which is done by this helper method. The parameters "value" and "values"
    are passed to it as they were received. This method will then perform the following checks, and throw a BaseError in
    case of failure:
      - check that exactly one of them contains data, but not both.
      - check that the values are usable, and not N/A

    Then, all values are transformed to PropertyElements and returned as a list. In case of a single "value", the
    resulting list contains the PropertyElement of this value.

    Args:
        value: "value" as received from the caller
        values: "values" as received from the caller
        name: name of the property (for better error messages)
        calling_resource: name of the resource (for better error messages)

    Returns:
        a list of PropertyElements
    """

    # reduce 'value' to None if it is not usable
    if not check_notna(value):
        value = None

    # reduce 'values' to None if it is not usable
    if values and not any([check_notna(val) for val in values]):
        values = None

    # assert that either "value" or "values" is usable, but not both at the same time
    if not value and not values:
        raise BaseError(f"ERROR in resource '{calling_resource}', property '{name}': 'value' and 'values' cannot both "
                        f"be empty")
    if value and values:
        raise BaseError(f"ERROR in resource '{calling_resource}', property '{name}': You cannot provide a 'value' and "
                        f"a 'values' at the same time!")

    # construct the resulting list
    result: list[PropertyElement] = list()

    if value:
        # make a PropertyElement out of it, if necessary
        if isinstance(value, PropertyElement):
            result.append(value)
        else:
            result.append(PropertyElement(value))
    elif values:
        # if "values" contains unusable elements, remove them
        multiple_values = [val for val in values if check_notna(val)]
        # make a PropertyElement out of them, if necessary
        for elem in multiple_values:
            if isinstance(elem, PropertyElement):
                result.append(elem)
            else:
                result.append(PropertyElement(elem))

    return result


def make_root(shortcode: str, default_ontology: str) -> etree.Element:
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


def append_permissions(root_element: etree.Element) -> etree.Element:
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
    res_default.append(ALLOW("CR", group="Creator"))
    res_default.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(res_default)

    res_restricted = PERMISSIONS(id="res-restricted")
    res_restricted.append(ALLOW("RV", group="UnknownUser"))
    res_restricted.append(ALLOW("V", group="KnownUser"))
    res_restricted.append(ALLOW("CR", group="Creator"))
    res_restricted.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(res_restricted)

    prop_default = PERMISSIONS(id="prop-default")
    prop_default.append(ALLOW("V", group="UnknownUser"))
    prop_default.append(ALLOW("V", group="KnownUser"))
    prop_default.append(ALLOW("CR", group="Creator"))
    prop_default.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(prop_default)

    prop_restricted = PERMISSIONS(id="prop-restricted")
    prop_restricted.append(ALLOW("RV", group="UnknownUser"))
    prop_restricted.append(ALLOW("V", group="KnownUser"))
    prop_restricted.append(ALLOW("CR", group="Creator"))
    prop_restricted.append(ALLOW("CR", group="ProjectAdmin"))
    root_element.append(prop_restricted)

    return root_element


def make_resource(
    label: str,
    restype: str,
    id: str,
    permissions: str = "res-default",
    ark: Optional[str] = None,
    iri: Optional[str] = None
) -> etree.Element:
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

    resource_ = etree.Element(
        "{%s}resource" % (xml_namespace_map[None]),
        **kwargs
    )
    return resource_


def make_bitstream_prop(
    path: str,
    permissions: str = "prop-default",
    calling_resource: str = ""
) -> etree.Element:
    """
    Creates a bitstream element that points to path.

    Args:
        path: path to a valid file that will be uploaded
        permissions: permissions string
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = make_resource(...)
        >>> resource.append(make_bitstream_prop("data/images/tree.jpg"))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#bitstream
    """

    if not os.path.isfile(path):
        warnings.warn(f"The following is not a valid path: {path} (resource '{calling_resource}')",
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
        raise BaseError(f"Invalid boolean format for prop '{name}' in resource '{calling_resource}': '{unformatted}'")


def make_boolean_prop(
    name: str,
    value: Union[PropertyElement, str, int, bool],
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <boolean-prop> from a boolean value. The value can be provided directly or inside a PropertyElement. The
    following formats are supported:
     - true: (True, "true", "True", "1", 1, "yes", "Yes")
     - false: (False, "false", "False", "0", 0, "no", "No")

    Unless provided as PropertyElement, the permission for every value is "prop-default".

    Args:
        name: the name of this property as defined in the onto
        value: a str/bool/int itself or inside a PropertyElement
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

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
        raise BaseError(f"Invalid boolean format for prop '{name}' in resource '{calling_resource}': '{value}'")

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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <color-prop> from one or more colors. The color(s) can be provided as string or as PropertyElement with a
    string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<color>`` child, use the param ``value``, to create more than one ``<color>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_color_prop(":testproperty", "#00ff66")
                <color-prop name=":testproperty">
                    <color permissions="prop-default">#00ff66</color>
                </color-prop>
        >>> make_color_prop(":testproperty", PropertyElement("#00ff66", permissions="prop-restricted", comment="example"))
                <color-prop name=":testproperty">
                    <color permissions="prop-restricted" comment="example">#00ff66</color>
                </color-prop>
        >>> make_color_prop(":testproperty", values=["#00ff66", "#000000"])
                <color-prop name=":testproperty">
                    <color permissions="prop-default">#00ff66</color>
                    <color permissions="prop-default">#000000</color>
                </color-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#color-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^#[0-9a-f]{6}$", str(val.value).strip(), flags=re.IGNORECASE):
            raise BaseError(f"Invalid color format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}color-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <date-prop> from one or more dates/date ranges. The date(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<date>`` child, use the param ``value``, to create more than one ``<date>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

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
        >>> make_date_prop(":testproperty", values=["GREGORIAN:CE:1930-09-02:CE:1930-09-03", "GREGORIAN:CE:1930-09-02:CE:1930-09-03"])
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
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\d{4})(-\d{1,2})?(-\d{1,2})?"
                         r"((:CE|:BCE)?(:\d{4})(-\d{1,2})?(-\d{1,2})?)?$", str(val.value).strip()):
            raise BaseError(f"Invalid date format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}date-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <decimal-prop> from one or more decimal numbers. The decimal(s) can be provided as string, float, or as
    PropertyElement with a string/float inside. If provided as string/float, the permission for every value is
    "prop-default".

    To create one ``<decimal>`` child, use the param ``value``, to create more than one ``<decimal>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/float/PropertyElement
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_decimal_prop(":testproperty", "3.14159")
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-default">3.14159</decimal>
                </decimal-prop>
        >>> make_decimal_prop(":testproperty", PropertyElement("3.14159", permissions="prop-restricted", comment="example"))
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-restricted" comment="example">3.14159</decimal>
                </decimal-prop>
        >>> make_decimal_prop(":testproperty", values=["3.14159", "2.718"])
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-default">3.14159</decimal>
                    <decimal permissions="prop-default">2.718</decimal>
                </decimal-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#decimal-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^\d+\.\d+$", str(val.value).strip()):
            raise BaseError(f"Invalid decimal format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}decimal-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}decimal" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_geometry_prop(
    name: str,
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <geometry-prop> from one or more areas of an image. The area(s) can be provided as JSON-string or as
    PropertyElement with the JSON-string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<geometry>`` child, use the param ``value``, to create more than one ``<geometry>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_geometry_prop(":testproperty", json_string)
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-default">{JSON}</geometry>
                </geometry-prop>
        >>> make_geometry_prop(":testproperty", PropertyElement(json_string, permissions="prop-restricted", comment="example"))
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-restricted" comment="example">{JSON}</geometry>
                </geometry-prop>
        >>> make_geometry_prop(":testproperty", values=[json_string1, json_string2])
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-default">{JSON}</geometry>
                    <geometry permissions="prop-default">{JSON}</geometry>
                </geometry-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#geometry-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        try:
            value_as_dict = json.loads(val.value)
            assert value_as_dict["type"] in ["rectangle", "circle"]
            assert isinstance(value_as_dict["points"], list)
        except (json.JSONDecodeError, TypeError, IndexError, KeyError, AssertionError):
            raise BaseError(f"Invalid geometry format for prop '{name}' in resource '{calling_resource}': "
                            f"'{val.value}'")

    # make xml structure of the value
    prop_ = etree.Element(
        "{%s}geometry-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str, int]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, int]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <geoname-prop> from one or more geonames.org IDs. The ID(s) can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permission for every value is
    "prop-default".

    To create one ``<geoname>`` child, use the param ``value``, to create more than one ``<geoname>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/int/PropertyElement
        values: an iterable of (usually distinct) strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_geoname_prop(":testproperty", "2761369")
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-default">2761369</geoname>
                </geoname-prop>
        >>> make_geoname_prop(":testproperty", PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-restricted" comment="example">2761369</geoname>
                </geoname-prop>
        >>> make_geoname_prop(":testproperty", values=["2761369", "1010101"])
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-default">2761369</geoname>
                    <geoname permissions="prop-default">1010101</geoname>
                </geoname-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#geoname-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^[0-9]+$", str(val.value)):
            raise BaseError(f"Invalid geoname format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    prop_ = etree.Element(
        "{%s}geoname-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str, int]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, int]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <integer-prop> from one or more integers. The integers can be provided as string, integer, or as
    PropertyElement with a string/integer inside. If provided as string/integer, the permission for every value is
    "prop-default".

    To create one ``<integer>`` child, use the param ``value``, to create more than one ``<integer>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/int/PropertyElement
        values: an iterable of (usually distinct) strings/ints/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_integer_prop(":testproperty", "2761369")
                <integer-prop name=":testproperty">
                    <integer permissions="prop-default">2761369</integer>
                </integer-prop>
        >>> make_integer_prop(":testproperty", PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <integer-prop name=":testproperty">
                    <integer permissions="prop-restricted" comment="example">2761369</integer>
                </integer-prop>
        >>> make_integer_prop(":testproperty", values=["2761369", "1010101"])
                <integer-prop name=":testproperty">
                    <integer permissions="prop-default">2761369</integer>
                    <integer permissions="prop-default">1010101</integer>
                </integer-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#integer-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^\d+$", str(val.value).strip()):
            raise BaseError(f"Invalid integer format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    prop_ = etree.Element(
        "{%s}integer-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = {"permissions": val.permissions}
        if check_notna(val.comment):
            kwargs["comment"] = val.comment
        value_ = etree.Element(
            "{%s}integer" % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = str(val.value)
        prop_.append(value_)

    return prop_


def make_interval_prop(
    name: str,
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <interval-prop> from one or more intervals. The interval(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<interval>`` child, use the param ``value``, to create more than one ``<interval>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_interval_prop(":testproperty", "61:3600")
                <interval-prop name=":testproperty">
                    <interval permissions="prop-default">61:3600</interval>
                </interval-prop>
        >>> make_interval_prop(":testproperty", PropertyElement("61:3600", permissions="prop-restricted", comment="example"))
                <interval-prop name=":testproperty">
                    <interval permissions="prop-restricted" comment="example">61:3600</interval>
                </interval-prop>
        >>> make_interval_prop(":testproperty", values=["61:3600", "60.5:120.5"])
                <interval-prop name=":testproperty">
                    <interval permissions="prop-default">61:3600</interval>
                    <interval permissions="prop-default">60.5:120.5</interval>
                </interval-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#interval-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.match(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)):([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))", str(val.value)):
            raise BaseError(f"Invalid integer format for prop '{name}' in resource '{calling_resource}': '{val.value}'")


    prop_ = etree.Element(
        "{%s}interval-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <list-prop> from one or more list items. The list item(s) can be provided as string or as PropertyElement
    with a string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<list>`` child, use the param ``value``, to create more than one ``<list>`` children, use ``values``.

    Args:
        list_name: the name of the list as defined in the onto
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_list_prop("mylist", ":testproperty", "first_node")
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-default">first_node</list>
                </list-prop>
        >>> make_list_prop("mylist", ":testproperty", PropertyElement("first_node", permissions="prop-restricted", comment="example"))
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-restricted" comment="example">first_node</list>
                </list-prop>
        >>> make_list_prop("mylist", ":testproperty", values=["first_node", "second_node"])
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-default">first_node</list>
                    <list permissions="prop-default">second_node</list>
                </list-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#list-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(f"Invalid list format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}list-prop" % (xml_namespace_map[None]),
        list=list_name,
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <resptr-prop> from one or more links to other resources. The links(s) can be provided as string or as
    PropertyElement with a string inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<resptr>`` child, use the param ``value``, to create more than one ``<resptr>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_resptr_prop(":testproperty", "resource_1")
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-default">resource_1</resptr>
                </resptr-prop>
        >>> make_resptr_prop(":testproperty", PropertyElement("resource_1", permissions="prop-restricted", comment="example"))
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-restricted" comment="example">resource_1</resptr>
                </resptr-prop>
        >>> make_resptr_prop(":testproperty", values=["resource_1", "resource_2"])
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-default">resource_1</resptr>
                    <resptr permissions="prop-default">resource_2</resptr>
                </resptr-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#resptr-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(f"Invalid resptr format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}resptr-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <text-prop> from one or more texts. The text(s) can be provided as string or as PropertyElement with a string
    inside. The default encoding is utf8. The default permission for every value is "prop-default".

    To create one ``<text>`` child, use the param ``value``, to create more than one ``<text>``
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">first text</text>
                </text-prop>
        >>> make_text_prop(":testproperty", PropertyElement("first text", permissions="prop-restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">first text</text>
                </text-prop>
        >>> make_text_prop(":testproperty", values=["first text", "second text"])
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">first text</text>
                    <text encoding="utf8" permissions="prop-default">second text</text>
                </text-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#text-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not isinstance(val.value, str) or not check_notna(val.value):
            raise BaseError(f"Invalid text format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}text-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str]] = None,
    values: Optional[Iterable[Union[PropertyElement, str]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make a <time-prop> from one or more datetime values of the form "2009-10-10T12:00:00-05:00". The time(s) can be
    provided as string or as PropertyElement with a string inside.  If provided as string, the permission for every
    value is "prop-default".

    To create one ``<time>`` child, use the param ``value``, to create more than one ``<time>`` children, use
    ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

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
        >>> make_time_prop(":testproperty", values=["2009-10-10T12:00:00-05:00", "1901-01-01T01:00:00-00:00"])
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
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        if not re.search(r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$", str(val.value)):
            raise BaseError(f"Invalid time format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}time-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    value: Optional[Union[PropertyElement, str, Any]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ""
) -> etree.Element:
    """
    Make an <uri-prop> from one or more URIs. The URI(s) can be provided as string or as PropertyElement with a string
    inside. If provided as string, the permission for every value is "prop-default".

    To create one ``<uri>`` child, use the param ``value``, to create more than one ``<uri>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement
        values: an iterable of (usually distinct) strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Returns:
        an etree.Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> make_uri_prop(":testproperty", "www.test.com")
                <uri-prop name=":testproperty">
                    <uri permissions="prop-default">www.test.com</uri>
                </uri-prop>
        >>> make_uri_prop(":testproperty", PropertyElement("www.test.com", permissions="prop-restricted", comment="example"))
                <uri-prop name=":testproperty">
                    <uri permissions="prop-restricted" comment="example">www.test.com</uri>
                </uri-prop>
        >>> make_uri_prop(":testproperty", values=["www.1.com", "www.2.com"])
                <uri-prop name=":testproperty">
                    <uri permissions="prop-default">www.1.com</uri>
                    <uri permissions="prop-default">www.2.com</uri>
                </uri-prop>

    See https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-xmlupload/#uri-prop
    """

    # check the input: prepare a list with valid values
    values_new = _check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
        if not regex.search(
            r"(?<scheme>[a-z][a-z0-9+.\-]*):(//(?<host>[\w_.\-\[\]:~]+)(?<port>:\d{0,6})?)(?<path>/[\p{L}%()_\-.~]*)*"
            r"(?<query>\?[\p{L}_.\-=]+)*(?<fragment>#[\p{L}_/\-~:.]*)?", str(val.value), flags=regex.UNICODE):
            raise BaseError(f"Invalid URI format for prop '{name}' in resource '{calling_resource}': '{val.value}'")

    # make xml structure of the valid values
    prop_ = etree.Element(
        "{%s}uri-prop" % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
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
    iri: Optional[str] = None
) -> etree.Element:
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
    iri: Optional[str] = None
) -> etree.Element:
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
    iri: Optional[str] = None
) -> etree.Element:
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
    project file (a.k.a. ontology). In order to create a correct XML for the `dsp-tools xmlupload`, a mapping is
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
    single_value_functions = [
        make_bitstream_prop,
        make_boolean_prop
    ]
    if re.search(r"\.csv$", datafile):
        # "utf_8_sig": an optional BOM at the start of the file will be skipped
        # let the "python" engine detect the separator
        main_df = pd.read_csv(datafile, encoding="utf_8_sig", dtype="str", sep=None, engine="python")
    elif re.search(r"(\.xls|\.xlsx)$", datafile):
        main_df = pd.read_excel(datafile, dtype="str")
    else:
        raise BaseError("The argument 'datafile' must have one of the extensions 'csv', 'xls', 'xlsx'")
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
        if check_notna(row["id"]):
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
            if resource_restype not in ["Annotation", "Region", "LinkObj"]:
                kwargs_resource["restype"] = resource_restype
                if check_notna(row.get("ark")):
                    kwargs_resource["ark"] = row["ark"]
                if check_notna(row.get("iri")):
                    kwargs_resource["iri"] = row["iri"]
                resource = make_resource(**kwargs_resource)
                if check_notna(row.get("file")):
                    file_permissions = row.get("file permissions")
                    if not check_notna(file_permissions):
                        file_permissions = "prop-default" if resource_permissions == "res-default" else "prop-restricted"
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
                raise BaseError(f"Invalid prop type for property {row['prop name']} in resource {resource_id}")
            make_prop_function = proptype_2_function[row["prop type"]]

            # every property contains i elements, which are represented in the Excel as groups of
            # columns named {i_value, i_encoding, i_res ref, i_permissions, i_comment}. Depending
            # on the property type, some of these items are NA.
            # Thus, prepare list of PropertyElement objects, with each PropertyElement containing only
            # the existing items.
            property_elements: list[PropertyElement] = []
            for i in range(1, max_prop_count + 1):
                value = row[f"{i}_value"]
                if check_notna(value):
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

            # create the property and append it to resource
            kwargs_propfunc: dict[str, Union[str, PropertyElement, list[PropertyElement]]] = {
                "name": row["prop name"],
                "calling_resource": resource_id
            }
            if len(property_elements) == 1:
                kwargs_propfunc["value"] = property_elements[0]
            else:
                kwargs_propfunc["values"] = property_elements
            if check_notna(row["prop list"]):
                kwargs_propfunc["list_name"] = str(row["prop list"])

            resource.append(make_prop_function(**kwargs_propfunc))

    # append the resource of the very last iteration of the for loop
    root.append(resource)

    # write file
    # ----------
    write_xml(root, f"{default_ontology}-data.xml")
    print(f"XML file successfully created at {default_ontology}-data.xml")
