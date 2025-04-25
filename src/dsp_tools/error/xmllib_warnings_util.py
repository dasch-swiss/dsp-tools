import inspect
import warnings
from typing import Any

import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning


def emit_xmllib_input_info(msg: MessageInfo) -> None:
    function_trace = _get_calling_code_context()
    msg_str = get_user_message_string(msg, function_trace)
    warnings.warn(XmllibInputInfo(msg_str))


def emit_xmllib_input_warning(msg: MessageInfo) -> None:
    function_trace = _get_calling_code_context()
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
        field_=value_field,
    )
    emit_xmllib_input_warning(msg_info)


def _get_calling_code_context() -> str | None:
    all_stack_frames = inspect.stack()
    frame_files = [x.filename for x in all_stack_frames]
    calling_func_index = _get_stack_frame_number(frame_files)
    if calling_func_index == -1:
        return None
    user_frame_info = all_stack_frames.pop(calling_func_index)
    file_name = user_frame_info.filename.rsplit("/", 1)[1]
    return f"{file_name}:{user_frame_info.lineno}"


def _get_stack_frame_number(file_names: list[str]) -> int:
    calling_func_index = -1
    for file in file_names:
        if _filter_stack_frames(file):
            calling_func_index += 1
        else:
            break
    return calling_func_index


def _filter_stack_frames(file_path: str) -> bool:
    dsp_tools_path = r"\/dsp[-_]tools\/(test|xmllib|error)\/"
    if regex.search(dsp_tools_path, file_path):
        return True
    elif regex.search(r"^<[a-zA-Z]+>$", file_path):
        return True
    return False


def get_user_message_string(msg: MessageInfo, function_trace: str | None) -> str:
    str_list = [f"Trace '{function_trace}'"] if function_trace else []
    if msg.resource_id:
        str_list.append(f"Resource ID '{msg.resource_id}'")
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    if msg.field_:
        str_list.append(f"Field '{msg.field_}'")
    str_list.append(msg.message)
    return " | ".join(str_list)
