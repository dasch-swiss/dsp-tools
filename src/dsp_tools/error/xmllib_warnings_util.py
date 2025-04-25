import inspect
import warnings

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
    calling_func_index = 0
    for trc in all_stack_frames:
        if "dsp_tools/error/" in trc.filename:
            calling_func_index += 1
        elif "dsp_tools/xmllib/" in trc.filename:
            calling_func_index += 1
    if calling_func_index == 0:
        return None
    user_frame_info = all_stack_frames.pop(calling_func_index)
    file_name = user_frame_info.filename.rsplit("/", 1)[1]
    return f"{file_name}:{user_frame_info.lineno}"


def get_user_message_string(msg: MessageInfo, function_trace: str | None) -> str:
    str_list = [f"Trace '{function_trace}'"] if function_trace else []
    str_list.append(f"Resource ID '{msg.resource_id}'")
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    if msg.field:
        str_list.append(f"Field '{msg.field}'")
    str_list.append(msg.message)
    return " | ".join(str_list)
