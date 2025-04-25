# mypy: disable-error-code="method-assign,no-untyped-def"
import pytest
import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.error.xmllib_warnings_util import _filter_stack_frames
from dsp_tools.error.xmllib_warnings_util import _get_calling_code_context
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import get_user_message_string


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


def test_get_calling_code_context():
    result = _get_calling_code_context()
    assert isinstance(result, str)
    assert result.startswith("test_xmllib_warnings_util.py:")


class TestGetMessageString:
    def test_with_property(self):
        msg_info = MessageInfo("msg", "id", "prop")
        result = get_user_message_string(msg_info, None)
        expected = "Resource ID 'id' | Property 'prop' | msg"
        assert result == expected

    def test_with_field(self):
        msg_info = MessageInfo("msg", "id", field_="field")
        result = get_user_message_string(msg_info, None)
        expected = "Resource ID 'id' | Field 'field' | msg"
        assert result == expected

    def test_without_res_id(self):
        msg_info = MessageInfo("msg", field_="field")
        result = get_user_message_string(msg_info, None)
        expected = "Field 'field' | msg"
        assert result == expected

    def test_with_trace(self, message_info):
        result = get_user_message_string(message_info, "trace")
        expected = "Trace 'trace' | Resource ID 'id' | msg"
        assert result == expected

    def test_no_property(self, message_info):
        result = get_user_message_string(message_info, None)
        expected = "Resource ID 'id' | msg"
        assert result == expected


@pytest.mark.parametrize(
    ("f_path", "expected"),
    [
        ("", True),
    ],
)
def test_(f_path, expected):
    assert _filter_stack_frames(f_path) == expected
