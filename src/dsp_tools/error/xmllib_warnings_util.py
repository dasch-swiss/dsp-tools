import warnings

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning


def emit_xmllib_input_info(msg: MessageInfo) -> None:
    msg_str = _get_message_string(msg)
    warnings.warn(XmllibInputInfo(msg_str))


def emit_xmllib_input_warning(msg: MessageInfo) -> None:
    msg_str = _get_message_string(msg)
    warnings.warn(XmllibInputWarning(msg_str))


def _get_message_string(msg: MessageInfo) -> str:
    str_list = [f"Resource ID '{msg.resource_id}'"]
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    str_list.append(msg.message)
    return " | ".join(str_list)
