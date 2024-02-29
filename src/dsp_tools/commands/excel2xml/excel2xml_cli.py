from __future__ import annotations

import warnings
from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Union

import pandas as pd
import regex
from lxml import etree

from dsp_tools.commands.excel2xml.excel2xml_lib import append_permissions
from dsp_tools.commands.excel2xml.excel2xml_lib import make_annotation
from dsp_tools.commands.excel2xml.excel2xml_lib import make_bitstream_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_boolean_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_color_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_date_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_decimal_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_geometry_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_geoname_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_integer_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_interval_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_link
from dsp_tools.commands.excel2xml.excel2xml_lib import make_list_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_region
from dsp_tools.commands.excel2xml.excel2xml_lib import make_resource
from dsp_tools.commands.excel2xml.excel2xml_lib import make_resptr_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_root
from dsp_tools.commands.excel2xml.excel2xml_lib import make_text_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import make_uri_prop
from dsp_tools.commands.excel2xml.excel2xml_lib import write_xml
from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.shared import check_notna

# ruff: noqa: E501 (line-too-long)


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
    if regex.search(r"\.csv$", datafile):
        dataframe = pd.read_csv(
            filepath_or_buffer=datafile,
            encoding="utf_8_sig",  # utf_8_sig is the default encoding of Excel
            dtype="str",
            sep=None,
            engine="python",  # let the "python" engine detect the separator
        )
    elif regex.search(r"(\.xls|\.xlsx)$", datafile):
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
    dataframe = dataframe.map(
        lambda x: x if pd.notna(x) and regex.search(r"[\p{L}\d_!?\-]", str(x), flags=regex.U) else pd.NA
    )

    # remove empty columns/rows
    dataframe = dataframe.dropna(axis="columns", how="all")
    dataframe = dataframe.dropna(axis="index", how="all")

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
        is_resource = check_notna(row["id"])
        is_property = check_notna(row["prop name"])
        match is_resource, is_property:
            case (True, True) | (False, False):  # either the row is a resource-row or a property-row, but not both
                raise BaseError(
                    f"Exactly 1 of the 2 columns 'id' and 'prop name' must be filled. "
                    f"Excel row {row_number} has too many/too less entries:\n"
                    f"id:        '{row['id']}'\n"
                    f"prop name: '{row['prop name']}'"
                )
            case True, False:  # this is a resource-row
                # the previous resource is finished, a new resource begins: append the previous to the resulting list
                # in all cases (except for the very first iteration), a previous resource exists
                if resource is not None:
                    resources.append(resource)
                resource = _convert_resource_row_to_xml(row_number=row_number, row=row)
            case False, True:  # this is a property-row
                if resource is None:
                    raise BaseError(
                        "The first row of your Excel/CSV is invalid. "
                        "The first row must define a resource, not a property."
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

    Warning:
        if the file permissions are missing and cannot be deduced from the resource permissions

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
            file_permissions = ""
            warnings.warn(
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

    Warning:
        if a mandatory cell is missing

    Returns:
        the resource element created from the row
    """
    # read and check the mandatory columns
    resource_id = row["id"]
    resource_label = row.get("label")
    if pd.isna([resource_label]):
        resource_label = ""
        warnings.warn(f"Missing label for resource '{resource_id}' (Excel row {row_number})")
    elif not check_notna(resource_label):
        warnings.warn(
            f"The label of resource '{resource_id}' looks suspicious: '{resource_label}' (Excel row {row_number})"
        )
    resource_restype = row.get("restype")
    if not check_notna(resource_restype):
        resource_restype = ""
        warnings.warn(f"Missing restype for resource '{resource_id}' (Excel row {row_number})")
    resource_permissions = row.get("permissions")
    if not check_notna(resource_permissions):
        resource_permissions = ""
        warnings.warn(f"Missing permissions for resource '{resource_id}' (Excel row {row_number})")

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
        with warnings.catch_warnings():  # prevent dublette warnings: most problems were already checked above
            warnings.filterwarnings("ignore")
            resource = make_region(**kwargs_resource)
    elif resource_restype == "Annotation":
        with warnings.catch_warnings():  # prevent dublette warnings: most problems were already checked above
            warnings.filterwarnings("ignore")
            resource = make_annotation(**kwargs_resource)
    elif resource_restype == "LinkObj":
        with warnings.catch_warnings():  # prevent dublette warnings: most problems were already checked above
            warnings.filterwarnings("ignore")
            resource = make_link(**kwargs_resource)
    else:
        kwargs_resource["restype"] = resource_restype
        with warnings.catch_warnings():  # prevent dublette warnings: most problems were already checked above
            warnings.filterwarnings("ignore")
            resource = make_resource(**kwargs_resource)
        with warnings.catch_warnings():  # ignore only the warnings about not existing files
            warnings.filterwarnings("ignore", message=".*path doesn't point to a file.*")
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
    return proptype_2_function[row["prop type"]]


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

    Warning:
        if a mandatory cell is missing, or if there are too many/too few values per property

    Returns:
        list of PropertyElement objects
    """
    property_elements: list[PropertyElement] = []
    for i in range(1, max_num_of_props + 1):
        value = row[f"{i}_value"]
        if pd.isna(value):
            # issue a warning if other cells of this property element are not empty
            # if all other cells are empty, continue with next property element
            other_cell_headers = [f"{i}_{x}" for x in ["encoding", "permissions", "comment"]]
            notna_cell_headers = [x for x in other_cell_headers if check_notna(row.get(x))]
            if notna_cell_headers_str := ", ".join([f"'{x}'" for x in notna_cell_headers]):
                warnings.warn(
                    f"Error in resource '{resource_id}': Excel row {row_number} has an entry "
                    f"in column(s) {notna_cell_headers_str}, but not in '{i}_value'. "
                    r"Please note that cell contents that don't meet the requirements of the regex [\p{L}\d_!?\-] "
                    "are considered inexistent."
                )
            continue

        # construct a PropertyElement from this property element
        kwargs_propelem = {"value": value, "permissions": str(row.get(f"{i}_permissions"))}
        if not check_notna(row.get(f"{i}_permissions")):
            warnings.warn(
                f"Resource '{resource_id}': "
                f"Missing permissions in column '{i}_permissions' of property '{row['prop name']}'"
            )
        if check_notna(row.get(f"{i}_comment")):
            kwargs_propelem["comment"] = str(row[f"{i}_comment"])
        if check_notna(row.get(f"{i}_encoding")):
            kwargs_propelem["encoding"] = str(row[f"{i}_encoding"])
        property_elements.append(PropertyElement(**kwargs_propelem))

    # validate the end result before returning it
    if not property_elements:
        warnings.warn(
            f"At least one value per property is required, "
            f"but resource '{resource_id}', property '{row['prop name']}' (Excel row {row_number}) doesn't contain any values."
        )
    if row.get("prop type") == "boolean-prop" and len(property_elements) > 1:
        warnings.warn(
            f"A <boolean-prop> can only have a single value, "
            f"but resource '{resource_id}', property '{row['prop name']}' (Excel row {row_number}) contains more than one value."
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
    return _create_property(
        make_prop_function=make_prop_function,
        row=row,
        property_elements=property_elements,
        resource_id=resource_id,
    )


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
        "value": property_elements[0] if row.get("prop type") == "boolean-prop" else property_elements,
    }

    if check_notna(row.get("prop list")):
        kwargs_propfunc["list_name"] = str(row["prop list"])

    return make_prop_function(**kwargs_propfunc)


def excel2xml(
    datafile: str,
    shortcode: str,
    default_ontology: str,
) -> tuple[bool, list[warnings.WarningMessage]]:
    """
    This is a method that is called from the command line.
    It isn't intended to be used in a Python script.
    It takes a tabular data source in CSV/XLS(X) format that is formatted according to the specifications,
    and transforms it into a DSP-conforming XML file
    that can be uploaded to a DSP server with the xmlupload command.
    The output file is saved in the current working directory,
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
    success = True
    dataframe = _read_cli_input_file(datafile)
    dataframe = _validate_and_prepare_cli_input_file(dataframe)
    last_column_title = str(list(dataframe)[-1])  # last column title, in the format "i_comment"
    max_num_of_props = int(last_column_title.split("_")[0])
    output_file = Path(f"{default_ontology}-data.xml")

    root = make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = append_permissions(root)

    with warnings.catch_warnings(record=True) as catched_warnings:
        resources = _convert_rows_to_xml(
            dataframe=dataframe,
            max_num_of_props=max_num_of_props,
        )
        for resource in resources:
            root.append(resource)
        write_xml(root, output_file)
        if len(catched_warnings) > 0:
            success = False
            for warning in catched_warnings:
                print(f"WARNING: {warning.message}")

    if success:
        print(f"XML file successfully written to '{output_file!s}'")
    else:
        red = "\033[31m"
        end = "\033[0m"
        print(
            f"{red}Some problems occurred. The XML file was written to '{output_file!s}', but it might be corrupt{end}"
        )

    return success, catched_warnings
