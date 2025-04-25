import inspect
import warnings

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


def _get_calling_code_context() -> str | None:
    all_stack_frames = inspect.stack()
    frame_files = [x.filename for x in all_stack_frames]
    calling_func_index = _get_stack_frame_number(frame_files)
    if calling_func_index == 0:
        return None
    user_frame_info = all_stack_frames.pop(calling_func_index)
    file_name = user_frame_info.filename.rsplit("/", 1)[1]
    return f"{file_name}:{user_frame_info.lineno}"


def _get_stack_frame_number(file_names: list[str]) -> int:
    calling_func_index = 0
    for file in file_names:
        if _filter_stack_frames(file):
            calling_func_index += 1
        else:
            break
    return calling_func_index


def _filter_stack_frames(file_path: str) -> bool:
    if "dsp_tools/error/" in file_path:
        return True
    elif "dsp_tools/xmllib/" in file_path:
        return True
    elif "dsp_tools/test/" in file_path:
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
