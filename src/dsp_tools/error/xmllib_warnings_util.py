import csv
import inspect
import os
import warnings
from pathlib import Path
from typing import Any
from typing import Never

import regex
from dotenv import load_dotenv

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning

load_dotenv()

WARNING_CSV_SAVEPATH: str | None = None


def configure_warning_logging():
    if file_path := os.getenv("WARNING_CSV_SAVEPATH"):
        global WARNING_CSV_SAVEPATH
        WARNING_CSV_SAVEPATH = file_path
        if not Path(WARNING_CSV_SAVEPATH).is_file():
            new_row = ["File", "Message", "Resource ID", "Property", "Field"]
        else:
            new_row = ["****" for _ in range(5)]
        with open(WARNING_CSV_SAVEPATH, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(new_row)


def write_to_csv_if_configured(msg: MessageInfo, function_trace: str | None) -> None:
    if WARNING_CSV_SAVEPATH:
        new_row = []
        new_row.append(function_trace if function_trace else "")
        new_row.append(msg.message if msg.message else "")
        new_row.append(msg.resource_id if msg.resource_id else "")
        new_row.append(msg.prop_name if msg.prop_name else "")
        new_row.append(msg.field if msg.field else "")
        with open(WARNING_CSV_SAVEPATH, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(new_row)


def get_user_message_string(msg: MessageInfo, function_trace: str | None) -> str:
    str_list = [f"File '{function_trace}'"] if function_trace else []
    if msg.resource_id:
        str_list.append(f"Resource ID '{msg.resource_id}'")
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    if msg.field:
        str_list.append(f"Field '{msg.field}'")
    str_list.append(msg.message)
    return " | ".join(str_list)


def _get_calling_code_context() -> str | None:
    """
    Find file name and line number of the file that was written by the user.
    """
    all_stack_frames = inspect.stack()
    frame_files = [x.filename for x in all_stack_frames]
    calling_func_index = _get_stack_frame_number(frame_files)
    if calling_func_index == 0:
        return None
    user_frame_info = all_stack_frames.pop(calling_func_index)
    file_name = user_frame_info.filename.rsplit("/", 1)[1]
    return f"{file_name}:{user_frame_info.lineno}"


def _get_stack_frame_number(file_names: list[str]) -> int:
    """
    Get index number of first python file of the stack trace which is not any more in the dsp-tools code.
    This is the index of the first user python file.
    """
    calling_func_index = -1
    for file in file_names:
        if _filter_stack_frames(file):
            calling_func_index += 1
        else:
            calling_func_index += 1
            break
    return calling_func_index


def _filter_stack_frames(file_path: str) -> bool:
    dsp_tools_path = r"\/dsp[-_]tools\/(xmllib|error)\/"
    if regex.search(dsp_tools_path, file_path):
        return True
    elif regex.search(r"^<[a-zA-Z]+>$", file_path):
        # This is for functions like str(), which appear in the stack trace as filename "<string>"
        return True
    return False


def raise_input_error(msg: MessageInfo) -> Never:
    function_trace = _get_calling_code_context()
    msg_str = get_user_message_string(msg, function_trace)
    raise InputError(msg_str)


def emit_xmllib_input_info(msg: MessageInfo) -> None:
    function_trace = _get_calling_code_context()
    msg_str = get_user_message_string(msg, function_trace)
    warnings.warn(XmllibInputInfo(msg_str))


def emit_xmllib_input_warning(msg: MessageInfo) -> None:
    function_trace = _get_calling_code_context()
    write_to_csv_if_configured(msg, function_trace)
    msg_str = get_user_message_string(msg, function_trace)
    warnings.warn(XmllibInputWarning(msg_str))


def emit_xmllib_input_type_mismatch_warning(
    *,
    expected_type: str,
    value: Any,
    res_id: str | None,
    value_field: str | None = None,
    prop_name: str | None = None,
) -> None:
    msg_info = MessageInfo(
        message=f"The input should be a valid {expected_type}, your input '{value}' does not match the type.",
        resource_id=res_id,
        prop_name=prop_name,
        field=value_field,
    )
    emit_xmllib_input_warning(msg_info)
