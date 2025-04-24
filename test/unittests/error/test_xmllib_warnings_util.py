from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import get_message_string


def test_with_property():
    msg_info = MessageInfo("msg", "id", "prop")
    result = get_message_string(msg_info)
    expected = "Resource ID 'id' | Property 'prop' | msg"
    assert result == expected


def test_no_property():
    msg_info = MessageInfo("msg", "id")
    result = get_message_string(msg_info)
    expected = "Resource ID 'id' | msg"
    assert result == expected
