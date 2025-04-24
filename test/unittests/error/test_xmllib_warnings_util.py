# mypy: disable-error-code="method-assign,no-untyped-def"
import pytest
import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.error.xmllib_warnings_util import _get_message_string
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning


@pytest.fixture
def message_info():
    return MessageInfo("msg", "id")


def test_emit_xmllib_input_info(message_info):
    expected = regex.escape("Resource ID 'id' | msg")
    with pytest.warns(XmllibInputInfo, match=expected):
        emit_xmllib_input_info(message_info)


def test_emit_xmllib_input_warning(message_info):
    expected = regex.escape("Resource ID 'id' | msg")
    with pytest.warns(XmllibInputWarning, match=expected):
        emit_xmllib_input_warning(message_info)


class TestGetMessageString:
    def test_with_property(self):
        msg_info = MessageInfo("msg", "id", "prop")
        result = _get_message_string(msg_info)
        expected = "Resource ID 'id' | Property 'prop' | msg"
        assert result == expected

    def test_no_property(self, message_info):
        result = _get_message_string(message_info)
        expected = "Resource ID 'id' | msg"
        assert result == expected
