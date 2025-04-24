from dsp_tools.error.xmllib_warnings import MessageInfo


def get_message_string(msg: MessageInfo) -> str:
    str_list = [f"Resource ID '{msg.resource_id}'"]
    if msg.prop_name:
        str_list.append(f"Property '{msg.prop_name}'")
    str_list.append(msg.message)
    return " | ".join(str_list)
