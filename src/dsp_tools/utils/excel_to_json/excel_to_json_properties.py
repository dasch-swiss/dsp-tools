import importlib.resources
import json
import warnings
from typing import Any, Optional
import jsonpath_ng.ext
import jsonschema
import regex
import pandas as pd
import numpy as np

import dsp_tools.utils.excel_to_json.utils as utl
from dsp_tools.models.exceptions import UserError

languages = ["en", "de", "fr", "it", "rm"]
language_label_col = ["label_en", "label_de", "label_fr", "label_it", "label_rm"]
mandatory_properties = ["name", "object", "gui_element"]


def _search_validation_error(
    list_properties: list[dict[str, Any]], excel_filename: str, validation_error: jsonschema.ValidationError
) -> str:
    """
    This function takes a list of properties, which are formatted as a dictionary and an error which was raised by the
    calling function. It then searches which exact location of the property caused the error. The results are added
    to a string which is used in the error that is raised in the calling function.

    Args:
        list_properties: List of properties
        excel_filename: Name of the Excel file
        validation_error: The error from the calling function

    Returns:
        A string which is used in the Error message that contains detailed information about the problem
    """
    err_msg_list = [f"The 'properties' section defined in the Excel file '{excel_filename}' did not pass validation."]
    json_path_to_property = regex.search(r"^\$\[(\d+)\]", validation_error.json_path)
    if json_path_to_property:
        # fmt: off
        wrong_property_name = (
            jsonpath_ng.ext.parse(json_path_to_property.group(0))
            .find(list_properties)[0]
            .value["name"]
        )
        # fmt: on
        excel_row = int(json_path_to_property.group(1)) + 2
        err_msg_list.append(f"The problematic property is '{wrong_property_name}' in Excel row {excel_row}.")
        affected_field = regex.search(
            r"name|labels|comments|super|subject|object|gui_element|gui_attributes",
            validation_error.json_path,
        )
        if affected_field:
            err_msg_list.append(
                f"The problem is that the column '{affected_field.group(0)}' has an invalid value: "
                f"{validation_error.message}"
            )
    else:
        err_msg_list.append(
            f"The error message is: {validation_error.message}\n" f"The error occurred at {validation_error.json_path}"
        )
    return "\n".join(err_msg_list)


def _validate_properties(
    properties_list: list[dict[str, Any]],
    excelfile: str,
) -> bool:
    """
    This function checks if the "properties" section of a JSON project file is valid, according to the JSON schema,
    and if the property names are unique.

    Args:
        properties_list: the "properties" section of a JSON project as a list of dicts
        excelfile: path to the Excel file containing the properties

    Raises:
        UserError: if the validation fails

    Returns:
        True if the "properties" section passed validation
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/properties-only.json").open(
        encoding="utf-8"
    ) as schema_file:
        properties_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=properties_list, schema=properties_schema)
    except jsonschema.ValidationError as err:
        err_msg = _search_validation_error(
            list_properties=properties_list, excel_filename=excelfile, validation_error=err
        )
        raise UserError(err_msg) from None
    return True


def _search_convert_numbers(value_str: str) -> str or int or float:
    """
    This function takes a string and searches if the string contains a float or an integer. In those cases, it converts
    the string to the corresponding data type. If it is not a float or integer, it returns the string as is.

    Args:
        value_str: The value which is checked and may be converted

    Returns:
        A int if the string was an integer, float if the string was a float or str if it was neither
    """
    if regex.search(r"^\d+\.\d+$", value_str):
        return float(value_str)
    elif regex.search(r"^\d+$", value_str):
        return int(value_str)
    else:
        return value_str


def _unpack_gui_attributes(gui_str: str) -> dict[str:str]:
    """
    This function takes a string which contains the gui_attributes if they are formatted according to the documentation
    a correct dictionary with the attribute name and its value is created. If the string is not formatted correctly,
    then the resulting list may not be in the expected format, this raises an IndexError. Only very broad errors
    can be caught with this function. Errors regarding the content will be diagnosed when the json is validated.

    Args:
        gui_str: A string containing the gui_attributes

    Returns:
        A dictionary with the gui_attribute name as key and the attribute as value.
    """
    # Create a list with several attributes
    gui_list = [x.strip() for x in gui_str.split(",") if not x.strip() == ""]
    # create a sub list with the kex value pair of the attribute if it is an empty string we exclude it.
    # this error will be detected when checking for the length of the lists
    gui_list = [[sub.strip() for sub in x.split(":") if sub.strip() != ""] for x in gui_list]
    # if not all sublist contain two items, something is wrong with the attribute
    if not all(len(sub) == 2 for sub in gui_list):
        raise IndexError
    return {sub[0]: sub[1] for sub in gui_list}


def _format_gui_attribute(attribute_str: str) -> dict[str : str or int or float]:
    """
    This function takes a string containing the information about the gui_attributes. First, a dictionary is created
    separating different attribute names and their values; in the second step it converts the numbers which are stored
    as strings into int or float data types.

    Args:
        attribute_str: A string containing the attributes

    Returns:
        A dictionary with the attribute name as a key and the attribute as value.
    """
    attribute_dict = _unpack_gui_attributes(gui_str=attribute_str)
    return {attrib: _search_convert_numbers(value_str=val) for attrib, val in attribute_dict.items()}


def _get_gui_attribute(df_row: pd.Series, row_num: int, excel_filename: str) -> dict[str : int or str or float]:
    """
    This function checks if the cell "gui_attributes" is empty. If it is, it returns None. If there is information,
    it extracts and formats it correctly. In case there is an unexpected format in the string, not according to the
    specification. The called function raises an IndexError. This error is caught, and a UserError is raised,
    which contains the row number and Excel file name.

    Args:
        df_row: Row of a pd.DataFrame
        row_num: The number of the row (index + 2)
        excel_filename: The name of the Excel file.

    Returns:
        A gui_attribute dictionary or None if there are no attributes

    Raises:
        UserError if there is a formatting error of the string
    """
    if pd.isnull(df_row["gui_attributes"]):
        return None
    # If the attribute is not in the correct format, a called function may raise an IndexError
    try:
        return _format_gui_attribute(attribute_str=df_row["gui_attributes"])
    except IndexError:
        raise UserError(
            f"Row {row_num} of Excel file {excel_filename} contains invalid data in column 'gui_attributes'.\n"
            "The expected format is '[attribute: value, attribute: value]'."
        ) from None


def _row2prop(prop_row: pd.Series, row_count: int, excel_filename: str) -> dict[str, Any]:
    """
    Takes a row from a pd.DataFrame, reads its content, and returns a dict object of the property

    Args:
        prop_row: row from a pd.DataFrame that defines a property
        row_count: row number of Excel file
        excel_filename: name of the original Excel file

    Returns:
        dict object of the property

    Raises:
        UserError if there are any formal mistakes in the "gui_attributes" column
    """
    _property = {x: prop_row[x] for x in mandatory_properties}
    # These are also mandatory but require formatting
    _property.update(
        {"labels": utl.get_labels(df_row=prop_row), "super": [s.strip() for s in prop_row["super"].split(",")]}
    )
    non_mandatory = {
        "comments": utl.get_comments(df_row=prop_row),
        "gui_attributes": _get_gui_attribute(df_row=prop_row, row_num=row_count, excel_filename=excel_filename),
    }
    # These functions may return None, this is checked before the update
    _property = utl.update_dict_ifnot_value_none(additional_dict=non_mandatory, to_update_dict=_property)
    return _property


def _check_gui_attributes(check_df: pd.DataFrame) -> dict[str : pd.Series] or None:
    """
    This function takes a pd.DataFrame and checks if the "gui_attributes" column is filled correctly. It does not check
    if the content is correct only if there is content, where mandatory or no content where it must be absent. If any
    or all of the checks fail, it creates a dictionary with a pd.Series as value which contains True for all rows where
    there is a problem otherwise, it returns None.

    Args:
        check_df: pd.DataFrame that should be checked

    Returns:
        A dictionary with a pd.Series that contains the information where there is a problem or None if all the
        checks passed.
    """
    mandatory_attributes = ["Spinbox", "List"]
    mandatory_check = utl.col_must_or_not_empty_based_on_other_col(
        check_df=check_df,
        substring_list=mandatory_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=True,
    )
    no_attributes = ["Checkbox", "Date", "Geonames", "Richtext", "TimeStamp"]
    no_attribute_check = utl.col_must_or_not_empty_based_on_other_col(
        check_df=check_df,
        substring_list=no_attributes,
        substring_colname="gui_element",
        check_empty_colname="gui_attributes",
        must_have_value=False,
    )
    # If neither has a problem, we return None
    if mandatory_check is None and no_attribute_check is None:
        return None
    # If both have problems, we combine the series
    elif mandatory_check is not None and no_attribute_check is not None:
        final_series = pd.Series(np.logical_or(mandatory_check, no_attribute_check))
    elif mandatory_check is not None:
        final_series = mandatory_check
    else:
        final_series = no_attribute_check
    # The boolean series is returned
    return {"wrong gui_attributes": final_series}


def _check_missing_values_in_row_raise_error(to_check_df: pd.DataFrame, excel_filename: str) -> None:
    """
    This function takes a pd.DataFrame which should be checked and the name of the original Excel file. It checks
    that columns which are in the "required_values" list contain a value for each row. Additionally, it checks that
    each row has at least one label in any language. Next, it checks if the gui_attributes comply. If all the checks
    are ok, then the dictionary is empty; in that case, the function ends without any effect. If any of the
    checks fail, the called functions return a dictionary with the column name as key, and the boolean pd.Series as
    value. True in the pd.Series denotes that there is a problem in that row. After all, the checks are done, the
    series is converted into row numbers. This information is added to the error message and a UserError is raised.

    Args:
        to_check_df: pd.DataFrame that is to be checked
        excel_filename: Name of the original Excel file

    Raises:
        UserError if any of the checks are failed
    """
    # Every row in these columns must have a value
    required_values = ["name", "super", "object", "gui_element"]
    # If there are no problems, it returns an empty dict
    missing_dict = utl.check_required_values(check_df=to_check_df, required_values_columns=required_values)
    # This checks if the label columns have at least one value per row
    missing_labels = utl.find_one_full_cell_in_cols(check_df=to_check_df, required_columns=language_label_col)
    # If everything is ok, we get None, otherwise we update the dict
    if missing_labels is not None:
        missing_dict.update({"label": missing_labels})
    # Some gui_element require a gui_attributes and others must not have one
    missing_gui_attributes = _check_gui_attributes(check_df=to_check_df)
    if missing_gui_attributes is not None:
        missing_dict.update(missing_gui_attributes)
    if missing_dict != {}:
        # Get the row numbers from the boolean series
        missing_dict = utl.get_wrong_row_numbers(wrong_row_dict=missing_dict, true_remains=True)
        error_str = "\n".join([f"Column Name:{k} Row Number: {v}" for k, v in missing_dict.items()])
        raise UserError(
            f"The file '{excel_filename}' is missing values in some rows. See below for more information:\n"
            f"{error_str}"
        )


def _do_property_excel_compliance(compliance_df: pd.DataFrame, excel_filename: str) -> None:
    """
    This function calls three separate functions which each checks if the pd.DataFrame is as we expect it. Each of
    these functions raises a UserError if there is a problem. If the checks do not fail, this function ends without
    an effect.

    Args:
        compliance_df: The pd.DataFrame that is checked
        excel_filename: The name of the original Excel file

    Raises:
        UserError if any of the checks fail
    """
    # If it does not pass any one of the tests, the function stops
    required_columns = {
        "name",
        "label_en",
        "label_de",
        "label_fr",
        "label_it",
        "label_rm",
        "comment_en",
        "comment_de",
        "comment_fr",
        "comment_it",
        "comment_rm",
        "super",
        "object",
        "gui_element",
        "gui_attributes",
    }
    utl.check_required_columns_raises_error(check_df=compliance_df, required_columns=required_columns)
    utl.check_duplicate_raise_error(check_df=compliance_df, duplicate_column="name")
    _check_missing_values_in_row_raise_error(to_check_df=compliance_df, excel_filename=excel_filename)


def _rename_deprecated_hlist(rename_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    """
    This function deals with Excel files that do conform to a previous format. If the old column names are not
    in the pd.DataFrame, then it returns it as was. The column "hlist" formerly contained the list name of the
    gui_element "ListValue". This information is transferred into the column "gui_attributes" if it exists, otherwise
    it is renamed.

    Args:
        rename_df: The pd.DataFrame which is checked and renamed
        excel_filename: Name of the original Excel file.

    Returns:
        Renamed pd.DataFrame or the original one

    Warnings:
        A warning for the user that the Excel file is not compliant with the new specifications
    """
    # If the deprecated feature is not in the df, then return the df
    if "hlist" not in rename_df.columns:
        return rename_df
    warnings.warn(
        f"The file '{excel_filename}' has a column 'hlist', which is deprecated. "
        f"Please use the column 'gui_attributes' for the attribute 'hlist'."
    )
    # Reformat the string according to the new convention
    rename_df["hlist"] = rename_df["hlist"].apply(lambda x: f"hlist:{x}" if isinstance(x, str) else x)
    # If gui_attributes already exists we have to merge the columns
    if "gui_attributes" in rename_df.columns:
        # In case there is a hlist, it is the only valid value in gui_attributes and has precedence
        rename_df["hlist"] = rename_df["hlist"].fillna(rename_df["gui_attributes"])
        rename_df.pop("gui_attributes")
    rename_df.rename(columns={"hlist": "gui_attributes"}, inplace=True)
    return rename_df


def _rename_deprecated_lang_cols(rename_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    """
    This function takes a pd.DataFrame and checks if the columns with the language label are named according to the old
    specifications. If they are, it renames them and informs the user that an old format is used. Otherwise, it
    returns the pd.Dataframe as was.

    Args:
        rename_df: pd.DataFrame, which is to be checked
        excel_filename: Name of the Excel file

    Returns:
        pd.DataFrame which has the columns renamed according to the new format

    Warnings:
        A warning for the user that the Excel file is not compliant with the new specifications
    """
    # If the columns are named correctly, return the df
    if set(language_label_col).issubset(set(rename_df.columns)):
        return rename_df
    if set(languages).issubset(set(rename_df.columns)):
        warnings.warn(
            f"The file '{excel_filename}' uses {languages} as column titles, which is deprecated. "
            f"Please use {[f'label_{lang}' for lang in languages]}"
        )
    rename_dict = dict(zip(languages, language_label_col))
    rename_df.rename(columns=rename_dict, inplace=True)
    return rename_df


def _rename_deprecated_columnnames(in_df: pd.DataFrame, excel_filename: str) -> pd.DataFrame:
    """
    This function calls two other functions that check and rename a deprecated Excel format. Afterward, the
    pd.DataFrame is compliant with the current format. In case the pd.DataFrame was already in the current format,
    the function passes without an effect.

    Args:
        in_df: pd.DataFrame that is checked and renamed
        excel_filename: Name of the original Excel

    Returns:
        pd.DataFrame that is renamed

    Warnings:
        Two user warnings if the pd.DataFrame is not according to the current specifications
    """
    in_df = _rename_deprecated_lang_cols(rename_df=in_df, excel_filename=excel_filename)
    in_df = _rename_deprecated_hlist(rename_df=in_df, excel_filename=excel_filename)
    return in_df


def excel2properties(
    excelfile: str,
    path_to_output_file: Optional[str] = None,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Converts properties described in an Excel file into a "properties" section which can be inserted into a JSON
    project file.

    Args:
        excelfile: path to the Excel file containing the properties
        path_to_output_file: if provided, the output is written into this JSON file

    Raises:
        UserError: if something went wrong

    Returns:
        a tuple consisting of the "properties" section as a Python list,
            and the success status (True if everything went well)
    """
    property_df = utl.read_excel_file(excel_filename=excelfile)

    property_df = _rename_deprecated_columnnames(in_df=property_df, excel_filename=excelfile)

    _do_property_excel_compliance(compliance_df=property_df, excel_filename=excelfile)

    # transform every row into a property
    props: list[dict[str, Any]] = []
    for index, row in property_df.iterrows():
        props.append(
            _row2prop(
                prop_row=row,
                row_count=int(str(index)),  # index is a label/index/hashable, but we need an int
                excel_filename=excelfile,
            )
        )

    # write final JSON file
    _validate_properties(properties_list=props, excelfile=excelfile)
    if path_to_output_file:
        with open(file=path_to_output_file, mode="w", encoding="utf-8") as file:
            json.dump(props, file, indent=4, ensure_ascii=False)
            print('"properties" section was created successfully and written to file:', path_to_output_file)

    return props, True
