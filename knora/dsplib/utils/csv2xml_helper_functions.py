import datetime
import json
import os
import re
import warnings
from collections.abc import Iterable
from typing import Any, Optional, Union

import pandas as pd
from lxml import etree
from lxml.builder import E

##############################
# global variables and classes
##############################
xml_namespace_map = {
    None: 'https://dasch.swiss/schema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class PropertyElement:
    value: str
    permissions: Optional[str]
    comment: Optional[str]
    encoding: Optional[str]

    def __init__(
        self, 
        value: Union[str, Any],
        permissions: Optional[Union[str, Any]] = 'prop-default', 
        comment: Optional[Union[str, Any]] = None, 
        encoding: Optional[Union[str, Any]] = None
    ):
        '''
        A PropertyElement object carries more information about a property value than just a plain string. 
        The "value" is the value that could be passed to a method as plain string. Use a PropertyElement
        instead to define more precisely what attributes your <text> tag (for example) will have.
        
        Args:
            value: This is the content that will be written between the <text></text> tags (for example)
            permissions: This is the permissions that your <text> tag (for example) will have
            comment: This is the comment that your <text> tag (for example) will have
            encoding: For <text> tags only. Can be 'xml' or 'utf8'. 

        Example:
            See the difference between the first and the second example:
            >>> make_text_prop(':testproperty', 'first text')
                <text-prop name=":testproperty">
                    <text encoding="utf8" permissions="prop-default">
                        first text
                    </text>
                </text-prop>
            >>> make_text_prop(':testproperty', PropertyElement('first text', permissions='prop-restricted', encoding='xml'))
                <text-prop name=":testproperty">
                    <text encoding="xml" permissions="prop-restricted">
                        first text
                    </text>
                </text-prop>
        '''
        self.value = str(value).strip()
        self.permissions = str(permissions)
        if comment:
            self.comment = str(comment)
        else:
            self.comment = None
        if encoding:
            self.encoding = str(encoding)
        else:
            self.encoding = None

    def __eq__(self, other):
        return all((
            self.value == other.value,
            self.permissions == other.permissions,
            self.comment == other.comment,
            self.encoding == other.encoding
        ))

    def __str__(self):
        return f'''PropertyElement with value={self.value}, permissions={self.permissions},
        comment={self.comment}, encoding={self.encoding}'''

    def __hash__(self):
        return hash(str(self))



###########
# functions
###########
def make_xs_id_compatible(string: Union[str, Any]) -> str:
    '''
    Make a string compatible with the constraints of xsd:ID as defined in 
    http://www.datypic.com/sc/xsd/t-xsd_ID.html. An xsd:ID cannot contain special characters, and it 
    must be unique in the document. For this reason, the illegal characters are not only replaced by 
    "_", but a random number is also appended to the result, so that it is unique.
    A string without any illegal characters will be returned unchanged.
    '''
    
    if not check_notna(string):
        return string
    string = str(string)
    
    # if start of string is neither letter nor underscore, add an underscore
    res = re.sub(r'^(?=[^A-Za-z_])', '_', string)

    # to make the xs id unique, create a pseudo-hash based on the position and kind of illegal 
    # characters found in the original string, and add it to the end of the result string 
    illegal_chars = ''
    for match in re.finditer(pattern = r'[^\d\w_\-\.]', string = string):
        illegal_chars = illegal_chars + str(ord(match.group(0))) + str(match.start())
    if illegal_chars != '':
        _hash = hash(f'{illegal_chars}{datetime.datetime.now()}')
        res = f'{res}_{_hash}'

    # replace all illegal characters by underscore
    res = re.sub(r'[^\d\w_\-\.]', '_', res)

    return res


def handle_warnings(msg: str):
    muted_warnings = [
        r'regex of warning you want to ignore',
    ]

    for muted_warning in muted_warnings:
        if re.search(pattern = muted_warning, string = msg):
            return
    
    warnings.warn(msg, stacklevel = 0)


def find_date_in_string(string: Union[str, Any], calling_resource = '') -> Union[str, None]:
    '''
    Checks if a string contains a date value (single date, or date range), and return the date 
    as DSP-formatted string. Return None if no date was found.

    Args:
        string: string to check
        calling_resource: the name of the parent resource (for better error messages)
    
    Returns:
        DSP-formatted date string, or None

    Example:
        if find_date_in_string(row['Epoch']):
            my_date = find_date_in_string(row['Epoch'])

    Currently supported date formats:
     - 2021-01-01 | 2015_01_02
     - 26.2.-24.3.1948
     - 31.4.2021 | 5/11/2021 | 1.12.1973 - 6.1.1974
     - March 9, 1908 | March 5,1908 | May 11, 1906
     - 1907 | 1886/7 | 1833/34 | 1849/1850

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#date-prop
    '''

    string = str(string)
    
    startdate: Any = None
    enddate: Any = None
    startyear: Any = None
    endyear: Any = None

    iso_date = re.search(r'((?:1[8-9][0-9][0-9])|(?:20[0-2][0-9]))[_-]([0-1][0-9])[_-]([0-3][0-9])', string)
        # template: 2021-01-01 or 2015_01_02
    eur_date_range = re.search(r'([0-3]?[0-9])[\./]([0-1]?[0-9])\.?-([0-3]?[0-9])[\./]([0-1]?[0-9])[\./]((?:1[8-9][0-9][0-9])|(?:20[0-2][0-9]))', string)
        # template: 26.2.-24.3.1948
    eur_date = list(re.finditer(r'([0-3]?[0-9])[\./]([0-1]?[0-9])[\./]((?:1[8-9][0-9][0-9])|(?:20[0-2][0-9]))', string))
        # template: 31.4.2021    5/11/2021    1.12.1973 - 6.1.1974
    monthname_date = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) ([0-3]?[0-9]), ?((?:1[8-9][0-9][0-9])|(?:20[0-2][0-9]))', string)
        # template: March 9, 1908   March 5,1908    May 11, 1906
    year_only = re.search(r'(?:1[8-9][0-9][0-9])|(?:20[0-2][0-9])', string)
        # template: 1907    1886/7    1833/34     1849/1850

    if iso_date and iso_date.lastindex == 3:
        year = int(iso_date.group(1))
        month = int(iso_date.group(2))
        day = int(iso_date.group(3))
        if year <= 2022 and month <= 12 and day <= 31:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        else:
            handle_warnings(f'Warning in resource {calling_resource}: '
            f'The following date was not parsed: {iso_date.group(0)}')

    elif eur_date_range and eur_date_range.lastindex == 5:
        startday = int(eur_date_range.group(1))
        startmonth = int(eur_date_range.group(2))
        endday = int(eur_date_range.group(3))
        endmonth = int(eur_date_range.group(4))
        startyear = int(eur_date_range.group(5))
        endyear = startyear
        if startyear <= 2022 and startmonth <= 12 and startday <= 31:
            startdate = datetime.date(startyear, startmonth, startday)
            enddate = datetime.date(endyear, endmonth, endday)
            if not enddate >= startdate:
                handle_warnings(f'Date parsing error in resource {calling_resource}: Enddate ({enddate.isoformat()}) '
                    f'is earlier than startdate ({startdate.isoformat()})')
                quit()
        else:
            handle_warnings(f'Warning in resource {calling_resource}: '
            f'The following date was not parsed: {eur_date_range.group(0)}')

    elif eur_date and eur_date[0].lastindex == 3:
        startyear = int(eur_date[0].group(3))
        startmonth = int(eur_date[0].group(2))
        startday = int(eur_date[0].group(1))
        if startyear <= 2022 and startmonth <= 12 and startday <= 31:
            startdate = datetime.date(startyear, startmonth, startday)
            enddate = startdate
        else:
            handle_warnings(f'Warning in resource {calling_resource}: '
            f'The following date was not parsed: {eur_date[0].group(0)}')
        if len(eur_date) == 2 and eur_date[1].lastindex == 3:
            endyear = int(eur_date[1].group(3))
            endmonth = int(eur_date[1].group(2))
            endday = int(eur_date[1].group(1))
            if endyear <= 2022 and endmonth <= 12 and endday <= 31:
                enddate = datetime.date(endyear, endmonth, endday)
                if not enddate >= startdate:
                    handle_warnings(f'Date parsing error in in resource {calling_resource}: '
                    f'Enddate ({enddate.isoformat()}) is earlier than startdate ({startdate.isoformat()})')
                    quit()
            else:
                handle_warnings(f'Warning in resource {calling_resource}: '
                f'The following date was not parsed: {eur_date[1].group(0)}')

    elif monthname_date and monthname_date.lastindex == 3:
        year = int(monthname_date.group(3))
        month = int(datetime.datetime.strptime(monthname_date.group(1), '%B').strftime('%m'))
            # parse full monthname with strptime (%B), then convert to number with strftime (%m)
        day = int(monthname_date.group(2))
        if year <= 2022 and month <= 12 and day <= 31:
            startdate = datetime.date(year, month, day)
            enddate = startdate
        else:
            handle_warnings(f'Warning in resource {calling_resource}: '
            f'The following date was not parsed: {monthname_date.group(0)}')
    
    elif year_only:
        startyear = year_only.group(0)
        endyear = startyear
        # optionally, there is a second year:
        secondyear = re.search(r'\d+/(\d+)', string)
        if secondyear:
            secondyear = secondyear.group(1)
            secondyear = startyear[0:-len(secondyear)] + secondyear
            if int(secondyear) != int(startyear) + 1:
                handle_warnings(f'Error in resource {calling_resource}: second year of {string} '
                f'could not be parsed, assume {int(startyear) + 1}')
            endyear = int(startyear) + 1

    if startdate is not None and enddate is not None:
        return f'GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}'
    elif startyear is not None and endyear is not None:
        return f'GREGORIAN:CE:{startyear}:CE:{endyear}'
    else:
        return None

    # Fancy, because auto-extracts many date formats out of strings, but discouraged, produces too many false positives:
    # datetime_obj = parser.parse(string, fuzzy = True, ignoretz = True)


def check_notna(string: Optional[Any]) -> bool:
    '''
    returns True if 'string' is a string with at least one word-character
    '''
    return pd.notna(string) and bool(re.search(r'\w', str(string)))


def check_and_prepare_values(
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]],
    values: Optional[Iterable[Union[PropertyElement, str, Any]]],
    name: Union[str, Any],
    calling_resource: str = ''
) -> list[PropertyElement]:
    
    if all([value is None or value is pd.NA, values is None or values is pd.NA]):
        handle_warnings(f'ERROR in resource "{calling_resource}", property "{name}": \n'
        f'"value" and "values" cannot be both empty')
        quit()
    
    if all([value is not None and value is not pd.NA, values is not None and values is not pd.NA]):
        handle_warnings(f'ERROR in resource "{calling_resource}", property "{name}": \n'
        f'You cannot provide a "value" and a "values" at the same time!')
        quit()
    
    if values is not None:
        valueslist = [v for v in values if v is not None]
        valueslist = sorted(set(valueslist), key=lambda x: valueslist.index(x))
        values_new: list[PropertyElement] = list()
        for x in valueslist:
            if isinstance(x, PropertyElement):
                values_new.append(x)
            else:
                values_new.append(PropertyElement(x))
    
    else: 
        if isinstance(value, PropertyElement):  
            values_new = [value, ]
        elif isinstance(value, str):
            assert value is not None
            values_new = [PropertyElement(value), ]
        elif isinstance(value, Iterable):
            valueslist = [v for v in value if v is not None]
            valueslist = sorted(set(valueslist), key=lambda x: valueslist.index(x))
            values_new: list[PropertyElement] = list()
            for x in valueslist:
                if isinstance(x, PropertyElement):
                    values_new.append(x)
                else:
                    values_new.append(PropertyElement(x))
            if len(values_new) > 1:
                handle_warnings(f'There are contradictory "{name}" values for "{calling_resource}": \n{[v.value for v in values_new]}')
                quit()
        else:
            handle_warnings('Wrong logic in method "check_and_prepare_values()". Please inform Johannes Nussbaum')
            quit()
    
    return values_new


def make_root(shortcode: str, default_ontology: str) -> etree._Element:
    '''
    Start your XML document with creating a root element. 

    Args:
        shortcode: The shortcode of this project as defined in the JSON onto file
        default ontology: As defined in the JSON onto file
    
    Returns: 
        The root element.
    
    Example:
        root = make_root(shortcode=shortcode, default_ontology=default_ontology)
        root = append_permissions(root)

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#the-root-element-knora
    '''

    root = etree.Element(
        _tag='{%s}knora' % (xml_namespace_map[None]),
        attrib={
            str(etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'schemaLocation')):
            'https://dasch.swiss/schema ' + \
            'https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd',
            'shortcode': shortcode,
            'default-ontology': default_ontology
        },
        nsmap=xml_namespace_map
    )
    return root


def append_permissions(root_element: etree._Element) -> etree._Element:
    '''
    Start your XML document with creating a root element, then call this method to append the permissions block.

    Args:
        root_element: The XML root element created by make_root()
    
    Returns: 
        The root element with the permissions appended
    
    Example:
        root = make_root(shortcode=shortcode, default_ontology=default_ontology)
        root = append_permissions(root)

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#describing-permissions-with-permissions-elements
    '''

    PERMISSIONS = E.permissions
    ALLOW = E.allow
    # lxml.builder.E is a more sophisticated element factory than etree.Element.
    # E.tag is equivalent to E('tag') and results in <tag>

    res_default = etree.Element('{%s}permissions' % (xml_namespace_map[None]), id='res-default')
    res_default.append(ALLOW('V', group='UnknownUser'))
    res_default.append(ALLOW('V', group='KnownUser'))
    res_default.append(ALLOW('CR', group='Creator'))
    res_default.append(ALLOW('CR', group='ProjectAdmin'))
    root_element.append(res_default)

    res_restricted = PERMISSIONS(id='res-restricted')
    res_restricted.append(ALLOW('RV', group='UnknownUser'))
    res_restricted.append(ALLOW('V', group='KnownUser'))
    res_restricted.append(ALLOW('CR', group='Creator'))
    res_restricted.append(ALLOW('CR', group='ProjectAdmin'))
    root_element.append(res_restricted)

    prop_default = PERMISSIONS(id='prop-default')
    prop_default.append(ALLOW('V', group='UnknownUser'))
    prop_default.append(ALLOW('V', group='KnownUser'))
    prop_default.append(ALLOW('CR', group='Creator'))
    prop_default.append(ALLOW('CR', group='ProjectAdmin'))
    root_element.append(prop_default)

    prop_restricted = PERMISSIONS(id='prop-restricted')
    prop_restricted.append(ALLOW('RV', group='UnknownUser'))
    prop_restricted.append(ALLOW('V', group='KnownUser'))
    prop_restricted.append(ALLOW('CR', group='Creator'))
    prop_restricted.append(ALLOW('CR', group='ProjectAdmin'))
    root_element.append(prop_restricted)

    return root_element


def make_resource(
    label: Union[str, Any],
    restype: Union[str, Any],
    id: Union[str, Any],
    ark: Union[str, Any, None] = None,
    permissions: Union[str, Any] = 'res-default'
) -> etree._Element:
    '''
    Creates an empty resource element, with the attributes as specified by the arguments

    Args:
        The arguments correspond 1:1 to the attributes of the <resource> element. 
    
    Returns: 
        The resource element, without any children, but with the attributes: 
        <resource label=label restype=restype id=id ark=ark permissions=permissions></resource>
    
    Example:
        resource = make_resource(...)
        resource.append(make_text_prop(...))
        root.append(resource)

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#describing-resources-with-the-resource-element
    '''

    kwargs = {
        'label': str(label),
        'restype': str(restype),
        'id': str(id),
        'permissions': str(permissions),
        'nsmap': xml_namespace_map
    }
    if ark is not None:
        kwargs['ark'] = str(ark)

    resource_ = etree.Element(
        '{%s}resource' % (xml_namespace_map[None]),
        **kwargs
    )
    return resource_


def make_bitstream_prop(path: Union[str, Any], calling_resource: str = '') -> etree._Element:
    '''
    Creates a bitstream element that points to path

    Args:
        path (str): path to a valid file that will be uploaded
        calling_resource (str): the name of the parent resource (for better error messages)
    
    Example:
        resource = make_resource(...)
        resource.append(make_bitstream_prop('data/images/tree.jpg'))
        root.append(resource)
    
    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#bitstream
    '''

    assert os.path.isfile(path), \
        f'The following is not the path to a valid file:\n' +\
        f'resource "{calling_resource}"\n' +\
        f'path     "{path}"'

    prop_ = etree.Element('{%s}bitstream' % (xml_namespace_map[None]), nsmap=xml_namespace_map)
    prop_.text = path
    return prop_


def format_bool(unformatted, name, calling_resource):
    true_values = ('true', '1', 1, 'yes')
    false_values = ('false', '0', 0, 'no', '', 'None')

    if unformatted in false_values or str(unformatted).lower() in false_values or pd.isna(unformatted):
        return 'false'
    elif unformatted in true_values or str(unformatted).lower() in true_values:
        return 'true'
    else:
        handle_warnings(
            f'{unformatted} is an invalid boolean format for property {name} in {calling_resource}'
        )
        quit()


def make_boolean_prop(
    name: Union[str, Any],
    value: Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]],
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <boolean-prop> from a boolean value. The value can be provided as PropertyElement
    or in one of the following formats:
     - true: ('true', 'True', '1', 1, 'Yes', 'yes')
     - false: ('false', 'False', '0', 0, 'No', 'no', '', 'None', pd.NA)

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_boolean_prop(':testproperty', '')``::

            ``      <boolean-prop name=":testproperty">
                        <boolean permissions="prop-default">false</boolean>
                    </boolean-prop>``

        - ``make_boolean_prop(':testproperty', PropertyElement('1', permissions='prop-restricted', comment='example'))``::

            ``      <boolean-prop name=":testproperty">
                        <boolean permissions="prop-restricted" comment="example">
                            true
                        </boolean>
                    </boolean-prop>``

        - ``make_boolean_prop(':testproperty', value=['false', '1'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    
    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#boolean-prop
    '''


    # check and validate input
    if isinstance(value, PropertyElement):
        value.value = format_bool(value.value, name, calling_resource)
        value_new = value
    elif isinstance(value, str) or not isinstance(value, Iterable):  # value is str | Any, but not Iterable
        value_new = PropertyElement(format_bool(value, name, calling_resource))
    elif isinstance(value, Iterable):
        value = [format_bool(item, name, calling_resource) for item in value if not isinstance(item, PropertyElement)]
        if len(set(value)) == 0:
            value_new = PropertyElement('false')
        elif len(set(value)) > 1:
            handle_warnings(f'There are contradictory {name} values for {calling_resource}: {set(value)}')
            quit()
        else:  # len(set(value)) == 1:
            val = list(value)[0]
            if isinstance(val, PropertyElement):
                val.value = format_bool(val.value, name, calling_resource)
                value_new = val
            else:  # val is str | Any
                value_new = PropertyElement(format_bool(val, name, calling_resource))
    else:
        handle_warnings('Wrong logic in method make_boolean_prop(). Please inform Johannes Nussbaum')
        quit()

    # make xml structure of the value
    prop_ = etree.Element(
        '{%s}boolean-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    kwargs = { 'permissions': value_new.permissions }
    if check_notna(value_new.comment):
        kwargs['comment'] = value_new.comment
    value_ = etree.Element(
        '{%s}boolean' % (xml_namespace_map[None]),
        **kwargs,
        nsmap=xml_namespace_map
    )
    value_.text = value_new.value
    prop_.append(value_)
    
    return prop_


def make_color_prop(
    name: Union[str, Any],
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <color-prop> from one or more colors. The color(s) can be provided as string or 
    as PropertyElement.

    To create one ``<color>`` child, use the param ``value``, to create more than one 
    ``<color>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_color_prop(':testproperty', '#00ff66')``::

            ``      <color-prop name=":testproperty">
                        <color permissions="prop-default">#00ff66</color>
                    </color-prop>``

        - ``make_color_prop(':testproperty', PropertyElement('#00ff66', permissions='prop-restricted', comment='example'))``::

            ``      <color-prop name=":testproperty">
                        <color permissions="prop-restricted" comment="example">
                            #00ff66
                        </color>
                    </color-prop>``

        - ``make_color_prop(':testproperty', values=['#00ff66', '#000000'])``::

            ``      <color-prop name=":testproperty">
                        <color permissions="prop-default">#00ff66</color>
                        <color permissions="prop-default">#000000</color>
                    </color-prop>``

        - ``make_color_prop(':testproperty', value=['#00ff66', '#000000'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#color-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert re.search(r'^#[0-9a-f]{6}$', val.value) is not None, \
            f'The following is not a valid color:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    prop_ = etree.Element(
        '{%s}color-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}color' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_date_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <date-prop> from one or more dates/date ranges. The date(s) can be provided as 
    string or as PropertyElement.

    To create one ``<date>`` child, use the param ``value``, to create more than one ``<date>`` 
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_date_prop(':testproperty', 'GREGORIAN:CE:2014-01-31')``::

            ``      <date-prop name=":testproperty">
                        <date permissions="prop-default">
                            GREGORIAN:CE:2014-01-31
                        </date>
                    </date-prop>``

        - ``make_date_prop(':testproperty', PropertyElement('GREGORIAN:CE:2014-01-31', permissions='prop-restricted', comment='example'))``::

            ``      <date-prop name=":testproperty">
                        <date permissions="prop-restricted" comment="example">
                            GREGORIAN:CE:2014-01-31
                        </date>
                    </date-prop>``

        - ``make_date_prop(':testproperty', values=['GREGORIAN:CE:1930-09-02:CE:1930-09-03', 'GREGORIAN:CE:1930-09-02:CE:1930-09-03'])``::

            ``      <date-prop name=":testproperty">
                        <date permissions="prop-default">
                            GREGORIAN:CE:1930-09-02:CE:1930-09-03
                        </date>
                        <date permissions="prop-default">
                            GREGORIAN:CE:1930-09-02:CE:1930-09-03
                        </date>
                    </date-prop>``

        - ``make_date_prop(':testproperty', value=['GREGORIAN:CE:2014-01-31', 'GREGORIAN:CE:1900-01-01'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#date-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        containsDate = isinstance(find_date_in_string(val.value), str)
        isDate = bool(re.search(
            r'(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\d{4})?(-\d{1,2})?(-\d{1,2})?'
            r'(:CE|:BCE)?(:\d{4})?(-\d{1,2})?(-\d{1,2})?', 
            val.value
        ))

        assert containsDate or isDate, \
            f'The following is not a valid calendar date:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    # make xml structure of the value
    prop_ = etree.Element(
        '{%s}date-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}date' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_decimal_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <decimal-prop> from one or more decimal numbers. The decimal(s) can be provided as 
    string, float, or as PropertyElement.

    To create one ``<decimal>`` child, use the param ``value``, to create more than one 
    ``<decimal>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_decimal_prop(':testproperty', '3.14159')``::

            ``      <decimal-prop name=":testproperty">
                        <decimal permissions="prop-default">3.14159</decimal>
                    </decimal-prop>``

        - ``make_decimal_prop(':testproperty', PropertyElement('3.14159', permissions='prop-restricted', comment='example'))``::

            ``      <decimal-prop name=":testproperty">
                        <decimal permissions="prop-restricted" comment="example">
                            3.14159
                        </decimal>
                    </decimal-prop>``

        - ``make_decimal_prop(':testproperty', values=['3.14159', '2.718'])``::

            ``      <decimal-prop name=":testproperty">
                        <decimal permissions="prop-default">3.14159</decimal>
                        <decimal permissions="prop-default">2.718</decimal>
                    </decimal-prop>``

        - ``make_decimal_prop(':testproperty', value=['3.14159', '2.718'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#decimal-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert str(float(val.value)) == val.value, \
            f'The following is not a valid decimal number:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    prop_ = etree.Element(
        '{%s}decimal-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}decimal' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_geometry_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <geometry-prop> from one or more areas of an image. The area(s) can be provided as JSON-string or as PropertyElement
    with the JSON-string as value.

    To create one ``<geometry>`` child, use the param ``value``, to create more than one ``<geometry>`` children, use ``values``.

    Warning: It is rather unusual to create a geometry-prop.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_geometry_prop(':testproperty', json_string)``::

            ``      <geometry-prop name=":testproperty">
                        <geometry permissions="prop-default">
                            {...json string...}
                        </geometry>
                    </geometry-prop>``

        - ``make_geometry_prop(':testproperty', PropertyElement(json_string, permissions='prop-restricted', comment='example'))``::

            ``      <geometry-prop name=":testproperty">
                        <geometry permissions="prop-restricted" comment="example">
                            {...json string...}
                        </geometry>
                    </geometry-prop>``

        - ``make_geometry_prop(':testproperty', values=[json_string1, json_string2])``::

            ``      <geometry-prop name=":testproperty">
                        <geometry permissions="prop-default">
                            {...json string 1...}
                        </geometry>
                        <geometry permissions="prop-default">
                            {...json string 2...}
                        </geometry>
                    </geometry-prop>``

        - ``make_geometry_prop(':testproperty', value=[json_string1, json_string2])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#geometry-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        try:
            json.loads(val.value)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                msg = str(e) + f'The following is not a valid Geometry JSON:\n' +\
                    f'resource: "{calling_resource}"\n' +\
                    f'property: "{name}"\n' +\
                    f'value:    "{val.value}"',
                doc=e.doc,
                pos=e.pos) from e

    prop_ = etree.Element(
        '{%s}geometry-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}geometry' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    return prop_


def make_geoname_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <geoname-prop> from one or more geonames.org IDs. The ID(s) can be provided as 
    string, integer, or as PropertyElement.

    To create one ``<geoname>`` child, use the param ``value``, to create more than one 
    ``<geoname>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_geoname_prop(':testproperty', '2761369')``::

            ``      <geoname-prop name=":testproperty">
                        <geoname permissions="prop-default">2761369</geoname>
                    </geoname-prop>``

        - ``make_geoname_prop(':testproperty', PropertyElement('2761369', permissions='prop-restricted', comment='example'))``::

            ``      <geoname-prop name=":testproperty">
                        <geoname permissions="prop-restricted" comment="example">
                            2761369
                        </geoname>
                    </geoname-prop>``

        - ``make_geoname_prop(':testproperty', values=['2761369', '1010101'])``::

            ``      <geoname-prop name=":testproperty">
                        <geoname permissions="prop-default">2761369</geoname>
                        <geoname permissions="prop-default">1010101</geoname>
                    </geoname-prop>``

        - ``make_geoname_prop(':testproperty', value=['2761369', '1010101'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#geoname-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert re.search(r'^[0-9]+$', val.value) is not None, \
            f'The following is not a valid geoname ID:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    prop_ = etree.Element(
        '{%s}geoname-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}geoname' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_integer_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <integer-prop> from one or more integers. The integers can be provided as string, 
    integer, or as PropertyElement.

    To create one ``<integer>`` child, use the param ``value``, to create more than one 
    ``<integer>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_integer_prop(':testproperty', '2761369')``::

            ``      <integer-prop name=":testproperty">
                        <integer permissions="prop-default">2761369</integer>
                    </integer-prop>``

        - ``make_integer_prop(':testproperty', PropertyElement('2761369', permissions='prop-restricted', comment='example'))``::

            ``      <integer-prop name=":testproperty">
                        <integer permissions="prop-restricted" comment="example">
                            2761369
                        </integer>
                    </integer-prop>``

        - ``make_integer_prop(':testproperty', values=['2761369', '1010101'])``::

            ``      <integer-prop name=":testproperty">
                        <integer permissions="prop-default">2761369</integer>
                        <integer permissions="prop-default">1010101</integer>
                    </integer-prop>``

        - ``make_integer_prop(':testproperty', value=['2761369', '1010101'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#integer-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert re.search(r'^\d+$', val.value) is not None, \
            f'The following is not a valid integer:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    prop_ = etree.Element(
        '{%s}integer-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}integer' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_interval_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <interval-prop> from one or more intervals. The interval(s) can be provided as 
    string or as PropertyElement.

    To create one ``<interval>`` child, use the param ``value``, to create more than one 
    ``<interval>`` children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_interval_prop(':testproperty', '61:3600')``::

            ``      <interval-prop name=":testproperty">
                        <interval permissions="prop-default">61:3600</interval>
                    </interval-prop>``

        - ``make_interval_prop(':testproperty', PropertyElement('61:3600', permissions='prop-restricted', comment='example'))``::

            ``      <interval-prop name=":testproperty">
                        <interval permissions="prop-restricted" comment="example">
                            61:3600
                        </interval>
                    </interval-prop>``

        - ``make_interval_prop(':testproperty', values=['61:3600', '60.5:120.5'])``::

            ``      <interval-prop name=":testproperty">
                        <interval permissions="prop-default">61:3600</interval>
                        <interval permissions="prop-default">60.5:120.5</interval>
                    </interval-prop>``

        - ``make_interval_prop(':testproperty', value=['61:3600', '60.5:120.5'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#interval-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert re.match(r'([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)):([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))', val.value) is not None, \
            f'The following is not a valid interval:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'

    prop_ = etree.Element(
        '{%s}interval-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}interval' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_list_prop(
    list_name: str,
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <list-prop> from one or more list items. The list item(s) can be provided as 
    string or as PropertyElement.

    To create one ``<list>`` child, use the param ``value``, to create more than one ``<list>`` 
    children, use ``values``.

    Args:
        list_name: the name of the list as defined in the onto
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_list_prop('mylist', ':testproperty', 'first_node')``::

            ``      <list-prop list="mylist" name=":testproperty">
                        <list permissions="prop-default">first_node</list>
                    </list-prop>``

        - ``make_list_prop('mylist', ':testproperty', PropertyElement('first_node', permissions='prop-restricted', comment='example'))``::

            ``      <list-prop list="mylist" name=":testproperty">
                        <list permissions="prop-restricted" comment="example">
                            first_node
                        </list>
                    </list-prop>``

        - ``make_list_prop('mylist', ':testproperty', values=['first_node', 'second_node'])``::

            ``      <list-prop list="mylist" name=":testproperty">
                        <list permissions="prop-default">first_node</list>
                        <list permissions="prop-default">second_node</list>
                    </list-prop>``

        - ``make_list_prop('mylist', ':testproperty', value=['first_node', 'second_node'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#list-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # make xml structure of the valid values
    prop_ = etree.Element(
        '{%s}list-prop' % (xml_namespace_map[None]),
        list=list_name,
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}list' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)

    return prop_


def make_resptr_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <resptr-prop> from one or more links to other resources. The links(s) can be provided as 
    string or as PropertyElement.

    To create one ``<resptr>`` child, use the param ``value``, to create more than one ``<resptr>`` 
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_resptr_prop(':testproperty', 'resource_1')``::

            ``      <resptr-prop name=":testproperty">
                        <resptr permissions="prop-default">resource_1</resptr>
                    </resptr-prop>``

        - ``make_resptr_prop(':testproperty', PropertyElement('resource_1', permissions='prop-restricted', comment='example'))``::

            ``      <resptr-prop name=":testproperty">
                        <resptr permissions="prop-restricted" comment="example">
                            resource_1
                        </resptr>
                    </resptr-prop>``

        - ``make_resptr_prop(':testproperty', values=['resource_1', 'resource_2'])``::

            ``      <resptr-prop name=":testproperty">
                        <resptr permissions="prop-default">resource_1</resptr>
                        <resptr permissions="prop-default">resource_2</resptr>
                    </resptr-prop>``

        - ``make_resptr_prop(':testproperty', value=['resource_1', 'resource_2'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#resptr-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    prop_ = etree.Element(
        '{%s}resptr-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}resptr' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_text_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <text-prop> from one or more texts. The text(s) can be provided as string or as 
    PropertyElement. For a string, the encoding is assumed to be utf8. 

    To create one ``<text>`` child, use the param ``value``, to create more than one ``<text>`` 
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        >>> make_text_prop(':testproperty', 'first text')
        <text-prop name=":testproperty">
            <text encoding="utf8" permissions="prop-default">first text</text>
        </text-prop>
        >>> make_text_prop(':testproperty', PropertyElement('first text', permissions='prop-restricted', encoding='xml'))
        <text-prop name=":testproperty">
            <text encoding="xml" permissions="prop-restricted">
                first text
            </text>
        </text-prop>
        >>> make_text_prop(':testproperty', values=['first text', 'second text'])
        <text-prop name=":testproperty">
            <text encoding="utf8" permissions="prop-default">first text</text>
            <text encoding="utf8" permissions="prop-default">second text</text>
        </text-prop>
        >>> make_text_prop(':testproperty', value=['first text', 'second text'])
        ERROR. Use this if some fields in your data source should be 
        equal, but you cannot trust your source. This method call will 
        only work if all items of "value" are identical.
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#text-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # make xml structure of the valid values
    prop_ = etree.Element(
        '{%s}text-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        if check_notna(val.encoding):
            kwargs['encoding'] = val.encoding
        else:
            kwargs['encoding'] = 'utf8'
        value_ = etree.Element(
            '{%s}text' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_time_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <time-prop> from one or more datetime values of the form "2009-10-10T12:00:00-05:00". 
    The time(s) can be provided as string or as PropertyElement.

    To create one ``<time>`` child, use the param ``value``, to create more than one ``<time>`` 
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_time_prop(':testproperty', '2009-10-10T12:00:00-05:00')``::

            ``      <time-prop name=":testproperty">
                        <time permissions="prop-default">
                            2009-10-10T12:00:00-05:00
                        </time>
                    </time-prop>``

        - ``make_time_prop(':testproperty', PropertyElement('2009-10-10T12:00:00-05:00', permissions='prop-restricted', comment='example'))``::

            ``      <time-prop name=":testproperty">
                        <time permissions="prop-restricted" comment="example">
                            2009-10-10T12:00:00-05:00
                        </time>
                    </time-prop>``

        - ``make_time_prop(':testproperty', values=['2009-10-10T12:00:00-05:00', '1901-01-01T01:00:00-00:00'])``::

            ``      <time-prop name=":testproperty">
                        <time permissions="prop-default">
                            2009-10-10T12:00:00-05:00
                        </time>
                        <time permissions="prop-default">
                            1901-01-01T01:00:00-00:002
                        </time>
                    </time-prop>``

        - ``make_time_prop(':testproperty', value=['2009-10-10T12:00:00-05:00', '1901-01-01T01:00:00-00:00'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#time-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # check value type
    for val in values_new:
        assert re.search(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$', val.value) is not None, \
            f'The following is not a valid time:\n' +\
            f'resource "{calling_resource}"\n' +\
            f'property "{name}"\n' +\
            f'value    "{val.value}"'
    
    # make xml structure of the valid values
    prop_ = etree.Element(
        '{%s}time-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}time' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_


def make_uri_prop(
    name: str,
    value: Optional[Union[PropertyElement, str, Any, Iterable[Union[PropertyElement, str, Any]]]] = None,
    values: Optional[Iterable[Union[PropertyElement, str, Any]]] = None,
    calling_resource: str = ''
) -> etree._Element:
    '''
    Make a <uri-prop> from one or more URIs. The URI(s) can be provided as string or as 
    PropertyElement.

    To create one ``<uri>`` child, use the param ``value``, to create more than one ``<uri>`` 
    children, use ``values``.

    Args:
        name: the name of this property as defined in the onto
        value: a string/PropertyElement, or an iterable of identical strings/PropertyElements
        values: an iterable of distinct strings/PropertyElements
        calling_resource: the name of the parent resource (for better error messages)

    Examples:
        - ``make_uri_prop(':testproperty', 'www.test.com')``::

            ``      <uri-prop name=":testproperty">
                        <uri permissions="prop-default">www.test.com</uri>
                    </uri-prop>``

        - ``make_uri_prop(':testproperty', PropertyElement('www.test.com', permissions='prop-restricted', comment='example'))``::

            ``      <uri-prop name=":testproperty">
                        <uri permissions="prop-restricted" comment="example">
                            www.test.com
                        </uri>
                    </uri-prop>``

        - ``make_uri_prop(':testproperty', values=['www.1.com', 'www.2.com'])``::

            ``      <uri-prop name=":testproperty">
                        <uri permissions="prop-default">www.1.com</uri>
                        <uri permissions="prop-default">www.2.com</uri>
                    </uri-prop>``

        - ``make_uri_prop(':testproperty', value=['www.1.com', 'www.2.com'])``::
       
            ``      ERROR. Use this if some fields in your data source should be 
                    equal, but you cannot trust your source. This method call will 
                    only work if all items of "value" are identical.``
    

    See https://dasch-swiss.github.io/dsp-tools/dsp-tools-xmlupload/#uri-prop
    '''

    # check the input: prepare a list with valid values
    values_new = check_and_prepare_values(
        value=value,
        values=values,
        name=name,
        calling_resource=calling_resource
    )

    # make xml structure of the valid values
    prop_ = etree.Element(
        '{%s}uri-prop' % (xml_namespace_map[None]),
        name=name,
        nsmap=xml_namespace_map
    )
    for val in values_new:
        kwargs = { 'permissions': val.permissions }
        if check_notna(val.comment):
            kwargs['comment'] = val.comment
        value_ = etree.Element(
            '{%s}uri' % (xml_namespace_map[None]),
            **kwargs,
            nsmap=xml_namespace_map
        )
        value_.text = val.value
        prop_.append(value_)
    
    return prop_
