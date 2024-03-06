import dataclasses
import datetime
import difflib
import json
import os
import uuid
import warnings
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Optional
from typing import Union

import regex
from lxml import etree
from lxml.builder import E
from regex import Match

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.models.datetimestamp import DateTimeStamp
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.date_util import is_full_date
from dsp_tools.utils.shared import check_notna
from dsp_tools.utils.shared import simplify_name
from dsp_tools.utils.uri_util import is_uri
from dsp_tools.utils.xml_validation import validate_xml

# ruff: noqa: E501 (line-too-long)


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
        an xsd ID based on the input string
    """

    if not isinstance(string, str) or not check_notna(string):
        raise BaseError(f"The input '{string}' cannot be transformed to an xsd:ID")

    # if start of string is neither letter nor underscore, add an underscore
    res = regex.sub(r"^(?=[^A-Za-z_])", "_", string)

    # replace all illegal characters by underscore
    res = regex.sub(r"[^\w_\-.]", "_", res, flags=regex.ASCII)

    # add uuid
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"

    return res


def _find_french_bc_date(
    string: str,
    lookbehind: str,
    lookahead: str,
) -> Optional[str]:
    french_bc_regex = r"av(?:\. |\.| )J\.?-?C\.?"
    if not regex.search(french_bc_regex, string):
        return None

    year_regex = r"\d{1,5}"
    sep_regex = r" ?- ?"

    year_range_regex = rf"{lookbehind}({year_regex}){sep_regex}({year_regex}) {french_bc_regex}{lookahead}"
    year_range = regex.search(year_range_regex, string)
    if year_range:
        start_year = int(year_range.group(1))
        end_year = int(year_range.group(2))
        if end_year > start_year:
            return None
        return f"GREGORIAN:BC:{start_year}:BC:{end_year}"

    single_year_regex = rf"{lookbehind}({year_regex}) {french_bc_regex}{lookahead}"
    single_year = regex.search(single_year_regex, string)
    if single_year:
        start_year = int(single_year.group(1))
        return f"GREGORIAN:BC:{start_year}:BC:{start_year}"

    return None


def find_date_in_string(string: str) -> Optional[str]:
    """
    Checks if a string contains a date value (single date, or date range),
    and returns the first found date as DSP-formatted string.
    Returns None if no date was found.

    Notes:
        - All dates are interpreted in the Christian era and the Gregorian calendar.
        - BC dates are only supported in French notation (e.g. 1000-900 av. J.-C.).
        - The years 0000-2999 are supported, in 3/4-digit form.
        - Dates written with slashes are always interpreted in a European manner: 5/11/2021 is the 5th of November.
        - In the European notation, 2-digit years are expanded to 4 digits, with the current year as watershed:
            - 30.4.24 -> 30.04.2024
            - 30.4.25 -> 30.04.1925

    Currently supported date formats:
        - 0476-09-04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 0476_09_04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 30.4.2021 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 30.4.21 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 5/11/2021 -> GREGORIAN:CE:2021-11-05:CE:2021-11-05
        - Jan 26, 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 28.2.-1.12.1515 -> GREGORIAN:CE:1515-02-28:CE:1515-12-01
        - 25.-26.2.0800 -> GREGORIAN:CE:0800-02-25:CE:0800-02-26
        - 1.9.2022-3.1.2024 -> GREGORIAN:CE:2022-09-01:CE:2024-01-03
        - 1848 -> GREGORIAN:CE:1848:CE:1848
        - 1849/1850 -> GREGORIAN:CE:1849:CE:1850
        - 1849/50 -> GREGORIAN:CE:1849:CE:1850
        - 1845-50 -> GREGORIAN:CE:1845:CE:1850
        - 840-50 -> GREGORIAN:CE:840:CE:850
        - 840-1 -> GREGORIAN:CE:840:CE:841
        - 1000-900 av. J.-C. -> GREGORIAN:BC:1000:BC:900
        - 45 av. J.-C. -> GREGORIAN:BC:45:BC:45

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
    try:
        return _find_date_in_string_throwing(string)
    except ValueError:
        return None


_months_dict = {
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


def _find_date_in_string_throwing(string: str) -> str | None:
    """
    This function is the same as find_date_in_string(), but may raise a ValueError instead of returning None.
    """
    year_regex = r"([0-2]?[0-9][0-9][0-9])"
    year_regex_2_or_4_digits = r"((?:[0-2]?[0-9])?[0-9][0-9])"
    month_regex = r"([0-1]?[0-9])"
    day_regex = r"([0-3]?[0-9])"
    sep_regex = r"[\./]"
    lookbehind = r"(?<![0-9A-Za-z])"
    lookahead = r"(?![0-9A-Za-z])"

    if french_bc_date := _find_french_bc_date(string=string, lookbehind=lookbehind, lookahead=lookahead):
        return french_bc_date

    # template: 2021-01-01 | 2015_01_02
    iso_date = regex.search(rf"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}", string)

    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range_regex = (
        rf"{lookbehind}"
        rf"{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex_2_or_4_digits}?)? ?(?:-|:|to) ?"
        rf"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}"
        rf"{lookahead}"
    )
    eur_date_range = regex.search(eur_date_range_regex, string)

    # template: 1.4.2021 | 5/11/2021
    eur_date_regex = rf"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}{lookahead}"
    eur_date = regex.search(
        eur_date_regex,
        string,
    )

    # template: March 9, 1908 | March5,1908 | May 11, 1906
    all_months = "|".join(_months_dict)
    monthname_date_regex = rf"{lookbehind}({all_months}) ?{day_regex}, ?{year_regex}{lookahead}"
    monthname_date = regex.search(monthname_date_regex, string)

    # template: 1849/50 | 1849-50 | 1849/1850
    year_range = regex.search(lookbehind + year_regex + r"[/-](\d{1,4})" + lookahead, string)

    # template: 1907
    year_only = regex.search(rf"{lookbehind}{year_regex}{lookahead}", string)

    res: str | None = None
    if iso_date:
        res = _from_iso_date(iso_date)
    elif eur_date_range:
        res = _from_eur_date_range(eur_date_range)
    elif eur_date:
        res = _from_eur_date(eur_date)
    elif monthname_date:
        res = _from_monthname_date(monthname_date)
    elif year_range:
        res = _from_year_range(year_range)
    elif year_only:
        year = int(year_only.group(0))
        res = f"GREGORIAN:CE:{year}:CE:{year}"
    return res


def _from_iso_date(iso_date: Match[str]) -> str:
    year = int(iso_date.group(1))
    month = int(iso_date.group(2))
    day = int(iso_date.group(3))
    date = datetime.date(year, month, day)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _expand_2_digit_year(year: int) -> int:
    current_year = datetime.date.today().year - 2000
    if year <= current_year:
        return year + 2000
    elif year <= 99:
        return year + 1900
    else:
        return year


def _from_eur_date_range(eur_date_range: Match[str]) -> str:
    startday = int(eur_date_range.group(1))
    startmonth = int(eur_date_range.group(2)) if eur_date_range.group(2) else int(eur_date_range.group(5))
    startyear = int(eur_date_range.group(3)) if eur_date_range.group(3) else int(eur_date_range.group(6))
    startyear = _expand_2_digit_year(startyear)
    endday = int(eur_date_range.group(4))
    endmonth = int(eur_date_range.group(5))
    endyear = int(eur_date_range.group(6))
    endyear = _expand_2_digit_year(endyear)
    startdate = datetime.date(startyear, startmonth, startday)
    enddate = datetime.date(endyear, endmonth, endday)
    if enddate < startdate:
        raise ValueError
    return f"GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}"


def _from_eur_date(eur_date: Match[str]) -> str:
    startday = int(eur_date.group(1))
    startmonth = int(eur_date.group(2))
    startyear = int(eur_date.group(3))
    startyear = _expand_2_digit_year(startyear)
    date = datetime.date(startyear, startmonth, startday)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _from_monthname_date(monthname_date: Match[str]) -> str:
    day = int(monthname_date.group(2))
    month = _months_dict[monthname_date.group(1)]
    year = int(monthname_date.group(3))
    date = datetime.date(year, month, day)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _from_year_range(year_range: Match[str]) -> str:
    startyear = int(year_range.group(1))
    endyear = int(year_range.group(2))
    if endyear // 10 == 0:
        # endyear is only 1-digit: add the first 2-3 digits of startyear
        endyear = startyear // 10 * 10 + endyear
    elif endyear // 100 == 0:
        # endyear is only 2-digit: add the first 1-2 digits of startyear
        endyear = startyear // 100 * 100 + endyear
    if endyear <= startyear:
        raise ValueError
    return f"GREGORIAN:CE:{startyear}:CE:{endyear}"


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
    Start building your XML document by creating the root element <knora>.

    Args:
        shortcode: The shortcode of this project as defined in the JSON project file
        default_ontology: one of the ontologies of the JSON project file

    Returns:
        The root element <knora>.

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
    After having created a root element, call this method to append the four permissions "res-default",
    "res-restricted", "prop-default", and "prop-restricted" to it. These four permissions are a good basis to
    start with, but remember that they can be adapted, and that other permissions can be defined instead of these.

    Args:
        root_element: The XML root element <knora> created by make_root()

    Returns:
        The root element with the four permission blocks appended

    Examples:
        >>> root = excel2xml.make_root(shortcode=shortcode, default_ontology=default_ontology)
        >>> root = excel2xml.append_permissions(root)

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


def make_resource(  # noqa: D417 (undocumented-param)
    label: str,
    restype: str,
    id: str,
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
        >>> resource = excel2xml.make_resource(...)
        >>> resource.append(excel2xml.make_text_prop(...))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#describing-resources-with-the-resource-element
    """
    if not check_notna(label):
        warnings.warn(f"WARNING: Your resource's label looks suspicious (resource with id '{id}' and label '{label}')")
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

    return etree.Element("{%s}resource" % xml_namespace_map[None], **kwargs)  # type: ignore[arg-type]


def make_bitstream_prop(
    path: Union[str, os.PathLike[Any]],
    permissions: str = "prop-default",
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

    Raises:
        Warning: if the path doesn't point to an existing file (only if check=True)

    Returns:
        an etree._Element that can be appended to the parent resource with resource.append(make_*_prop(...))

    Examples:
        >>> resource = excel2xml.make_resource(...)
        >>> resource.append(excel2xml.make_bitstream_prop("data/images/tree.jpg"))
        >>> root.append(resource)

    See https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#bitstream
    """

    if check and not Path(path).is_file():
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
        >>> excel2xml.make_boolean_prop(":testproperty", "no")
                <boolean-prop name=":testproperty">
                    <boolean permissions="prop-default">false</boolean>
                </boolean-prop>
        >>> excel2xml.make_boolean_prop(":testproperty", excel2xml.PropertyElement("1", permissions="prop-restricted", comment="example"))
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
        >>> excel2xml.make_color_prop(":testproperty", "#00ff66")
                <color-prop name=":testproperty">
                    <color permissions="prop-default">#00ff66</color>
                </color-prop>
        >>> excel2xml.make_color_prop(":testproperty", excel2xml.PropertyElement("#00ff66", permissions="prop-restricted", comment="example"))
                <color-prop name=":testproperty">
                    <color permissions="prop-restricted" comment="example">#00ff66</color>
                </color-prop>
        >>> excel2xml.make_color_prop(":testproperty", ["#00ff66", "#000000"])
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
        if not regex.search(r"^#[0-9a-f]{6}$", str(val.value).strip(), flags=regex.IGNORECASE):
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
        >>> excel2xml.make_date_prop(":testproperty", "GREGORIAN:CE:2014-01-31")
                <date-prop name=":testproperty">
                    <date permissions="prop-default">GREGORIAN:CE:2014-01-31</date>
                </date-prop>
        >>> excel2xml.make_date_prop(":testproperty", excel2xml.PropertyElement("GREGORIAN:CE:2014-01-31", permissions="prop-restricted", comment="example"))
                <date-prop name=":testproperty">
                    <date permissions="prop-restricted" comment="example">
                        GREGORIAN:CE:2014-01-31
                    </date>
                </date-prop>
        >>> excel2xml.make_date_prop(":testproperty", ["GREGORIAN:CE:1930-09-02:CE:1930-09-03", "GREGORIAN:CE:1930-09-02:CE:1930-09-03"])
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
    for val in values:
        if not is_full_date(str(val.value).strip()):
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
        >>> excel2xml.make_decimal_prop(":testproperty", "3.14159")
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-default">3.14159</decimal>
                </decimal-prop>
        >>> excel2xml.make_decimal_prop(":testproperty", excel2xml.PropertyElement("3.14159", permissions="prop-restricted", comment="example"))
                <decimal-prop name=":testproperty">
                    <decimal permissions="prop-restricted" comment="example">3.14159</decimal>
                </decimal-prop>
        >>> excel2xml.make_decimal_prop(":testproperty", ["3.14159", "2.718"])
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
        >>> excel2xml.make_geometry_prop(":testproperty", json_string)
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-default">{JSON}</geometry>
                </geometry-prop>
        >>> excel2xml.make_geometry_prop(":testproperty", excel2xml.PropertyElement(json_string, permissions="prop-restricted", comment="example"))
                <geometry-prop name=":testproperty">
                    <geometry permissions="prop-restricted" comment="example">{JSON}</geometry>
                </geometry-prop>
        >>> excel2xml.make_geometry_prop(":testproperty", [json_string1, json_string2])
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
            if value_as_dict["type"] not in ["rectangle", "circle", "polygon"]:
                raise BaseError(
                    f"Failed validation in resource '{calling_resource}', property '{name}': "
                    f"The 'type' of the JSON geometry object must be 'rectangle', 'circle', or 'polygon'."
                )
            if not isinstance(value_as_dict["points"], list):
                raise BaseError(
                    f"Failed validation in resource '{calling_resource}', property '{name}': "
                    f"The 'points'of the JSON geometry object must be a list of points."
                )
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
        >>> excel2xml.make_geoname_prop(":testproperty", "2761369")
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-default">2761369</geoname>
                </geoname-prop>
        >>> excel2xml.make_geoname_prop(":testproperty", excel2xml.PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <geoname-prop name=":testproperty">
                    <geoname permissions="prop-restricted" comment="example">2761369</geoname>
                </geoname-prop>
        >>> excel2xml.make_geoname_prop(":testproperty", ["2761369", "1010101"])
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
        if not regex.search(r"^[0-9]+$", str(val.value)):
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
        >>> excel2xml.make_integer_prop(":testproperty", "2761369")
                <integer-prop name=":testproperty">
                    <integer permissions="prop-default">2761369</integer>
                </integer-prop>
        >>> excel2xml.make_integer_prop(":testproperty", excel2xml.PropertyElement("2761369", permissions="prop-restricted", comment="example"))
                <integer-prop name=":testproperty">
                    <integer permissions="prop-restricted" comment="example">2761369</integer>
                </integer-prop>
        >>> excel2xml.make_integer_prop(":testproperty", ["2761369", "1010101"])
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
        >>> excel2xml.make_interval_prop(":testproperty", "61:3600")
                <interval-prop name=":testproperty">
                    <interval permissions="prop-default">61:3600</interval>
                </interval-prop>
        >>> excel2xml.make_interval_prop(":testproperty", excel2xml.PropertyElement("61:3600", permissions="prop-restricted", comment="example"))
                <interval-prop name=":testproperty">
                    <interval permissions="prop-restricted" comment="example">61:3600</interval>
                </interval-prop>
        >>> excel2xml.make_interval_prop(":testproperty", ["61:3600", "60.5:120.5"])
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
        if not regex.match(
            r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)):([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))",
            str(val.value),
        ):
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
        >>> excel2xml.make_list_prop("mylist", ":testproperty", "first_node")
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-default">first_node</list>
                </list-prop>
        >>> excel2xml.make_list_prop("mylist", ":testproperty", excel2xml.PropertyElement("first_node", permissions="prop-restricted", comment="example"))
                <list-prop list="mylist" name=":testproperty">
                    <list permissions="prop-restricted" comment="example">first_node</list>
                </list-prop>
        >>> excel2xml.make_list_prop("mylist", ":testproperty", ["first_node", "second_node"])
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
        >>> excel2xml.make_resptr_prop(":testproperty", "resource_1")
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-default">resource_1</resptr>
                </resptr-prop>
        >>> excel2xml.make_resptr_prop(":testproperty", excel2xml.PropertyElement("resource_1", permissions="prop-restricted", comment="example"))
                <resptr-prop name=":testproperty">
                    <resptr permissions="prop-restricted" comment="example">resource_1</resptr>
                </resptr-prop>
        >>> excel2xml.make_resptr_prop(":testproperty", ["resource_1", "resource_2"])
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
        >>> excel2xml.make_text_prop(":testproperty", "first text")
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">first text</text>
                </text-prop>
        >>> excel2xml.make_text_prop(":testproperty", excel2xml.PropertyElement("first text", permissions="prop-restricted", encoding="xml"))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">first text</text>
                </text-prop>
        >>> excel2xml.make_text_prop(":testproperty", ["first text", "second text"])
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
            escaped_text = _escape_reserved_chars(str(val.value))
            # enforce that the text is well-formed XML: serialize tag ...
            serialized = etree.tostring(value_, encoding="unicode")
            # ... insert text at the very end of the string, and add ending tag to the previously single <text/> tag ...
            serialized = regex.sub(r"/>$", f">{escaped_text}</text>", serialized)
            # ... try to parse it again
            try:
                value_ = etree.fromstring(serialized)
            except etree.XMLSyntaxError as err:
                msg = (
                    "The XML tags contained in a richtext property (encoding=xml) must be well-formed. "
                    "The special characters <, > and & are only allowed to construct a tag. "
                )
                if calling_resource:
                    msg += f"The error occurred in resource {calling_resource}, property {name}"
                msg += f"\nOriginal error message: {err.msg}"
                msg += f"\nEventual line/column numbers are relative to this serialized text: {serialized}"
                raise BaseError(msg) from None
        prop_.append(value_)

    return prop_


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
    lookahead = rf"(?!/?({allowed_tags_regex})>)"
    lookbehind = rf"(?<!</?({allowed_tags_regex}))"
    illegal_lt = rf"<{lookahead}"
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
        >>> excel2xml.make_time_prop(":testproperty", "2009-10-10T12:00:00-05:00")
                <time-prop name=":testproperty">
                    <time permissions="prop-default">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> excel2xml.make_time_prop(":testproperty", excel2xml.PropertyElement("2009-10-10T12:00:00-05:00", permissions="prop-restricted", comment="example"))
                <time-prop name=":testproperty">
                    <time permissions="prop-restricted" comment="example">
                        2009-10-10T12:00:00-05:00
                    </time>
                </time-prop>
        >>> excel2xml.make_time_prop(":testproperty", ["2009-10-10T12:00:00-05:00", "1901-01-01T01:00:00-00:00"])
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
        if not regex.search(validation_regex, str(val.value)):
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
        >>> excel2xml.make_uri_prop(":testproperty", "www.test.com")
                <uri-prop name=":testproperty">
                    <uri permissions="prop-default">www.test.com</uri>
                </uri-prop>
        >>> excel2xml.make_uri_prop(":testproperty", excel2xml.PropertyElement("www.test.com", permissions="prop-restricted", comment="example"))
                <uri-prop name=":testproperty">
                    <uri permissions="prop-restricted" comment="example">www.test.com</uri>
                </uri-prop>
        >>> excel2xml.make_uri_prop(":testproperty", ["www.1.com", "www.2.com"])
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
        if not is_uri(str(val.value)):
            raise BaseError(
                f"Failed validation in resource '{calling_resource}', property '{name}': "
                f"'{val.value}' is not a valid URI."
            )

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

    return etree.Element(
        "{%s}region" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )


def make_annotation(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
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
        >>> annotation = excel2xml.make_annotation("label", "id")
        >>> annotation.append(excel2xml.make_text_prop("hasComment", "This is a comment"))
        >>> annotation.append(excel2xml.make_resptr_prop("isAnnotationOf", "resource_0"))
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

    return etree.Element(
        "{%s}annotation" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )


def make_link(  # noqa: D417 (undocumented-param)
    label: str,
    id: str,
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

    return etree.Element(
        "{%s}link" % xml_namespace_map[None],
        **kwargs,  # type: ignore[arg-type]
    )


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
            excel_values_new.extend([x.strip() for x in val.split(sep) if x])

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
            warnings.warn(
                f"Did not find a close match to the excel list entry '{excel_value}' "
                f"among the values in the JSON project list '{list_name}'",
                stacklevel=2,
            )

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
        validate_xml(input_file=filepath)
        print(f"The XML file was successfully saved to {filepath}")
    except BaseError as err:
        warnings.warn(
            f"The XML file was successfully saved to {filepath}, "
            f"but the following Schema validation error(s) occurred: {err.message}"
        )
