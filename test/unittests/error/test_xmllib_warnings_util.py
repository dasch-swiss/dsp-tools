# mypy: disable-error-code="method-assign,no-untyped-def"
import pandas as pd
import pytest
import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings import XmllibInputInfo
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.error.xmllib_warnings_util import _filter_stack_frames
from dsp_tools.error.xmllib_warnings_util import _get_calling_code_context
from dsp_tools.error.xmllib_warnings_util import _get_stack_frame_number
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_info
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
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


def test_emit_xmllib_input_type_mismatch_warning():
    expected = regex.escape(
        "' | Resource ID 'id' | Field 'field' | "
        "The input should be a valid string, your input '<NA>' does not match the type."
    )
    with pytest.warns(XmllibInputWarning, match=expected):
        emit_xmllib_input_type_mismatch_warning(expected_type="string", value=pd.NA, res_id="id", value_field="field")


class TestGetMessageString:
    def test_with_property(self):
        msg_info = MessageInfo("msg", "id", "prop")
        result = get_user_message_string(msg_info, None)
        expected = "Resource ID 'id' | Property 'prop' | msg"
        assert result == expected

    def test_with_field(self):
        msg_info = MessageInfo("msg", "id", field="field")
        result = get_user_message_string(msg_info, None)
        expected = "Resource ID 'id' | Field 'field' | msg"
        assert result == expected

    def test_without_res_id(self):
        msg_info = MessageInfo("msg", field="field")
        result = get_user_message_string(msg_info, None)
        expected = "Field 'field' | msg"
        assert result == expected

    def test_with_trace(self, message_info):
        result = get_user_message_string(message_info, "trace")
        expected = "File 'trace' | Resource ID 'id' | msg"
        assert result == expected

    def test_no_property(self, message_info):
        result = get_user_message_string(message_info, None)
        expected = "Resource ID 'id' | msg"
        assert result == expected


class TestStackFrame:
    def test_get_calling_code_context(self):
        result = _get_calling_code_context()
        assert isinstance(result, str)
        assert regex.search(r"test_xmllib_warnings_util\.py:\d+", result)

    def test_get_stack_frame_number(self):
        file_paths = [
            "/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/error/xmllib_warnings_util.py",
            "/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/error/xmllib_warnings_util.py",
            "/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/xmllib/models/dsp_base_resources.py",
            "/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/xmllib/models/dsp_base_resources.py",
            "<string>",
            "/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/xmllib/models/dsp_base_resources.py",
            "/Users/UserName/repoLocation/dsp-tools/test/unittests/xmllib/models/test_dsp_base_resources.py",
            "/Users/UserName/repoLocation/dsp-tools/.venv/lib/python3.12/site-packages/_pytest/python.py",
            "/Users/UserName/Applications/PyCharm CE.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py",
        ]
        assert _get_stack_frame_number(file_paths) == 6

    def test_get_stack_frame_number_none(self):
        file_paths = [
            "/Users/UserName/repoLocation/dsp-tools/.venv/lib/python3.12/site-packages/_pytest/python.py",
            ("/Users/UserName/Applications/PyCharm CE.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py"),
        ]
        assert _get_stack_frame_number(file_paths) == 0

    @pytest.mark.parametrize(
        ("f_path", "expected"),
        [
            ("/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/error/xmllib_warnings_util.py", True),
            ("/Users/UserName/repoLocation/dsp-tools/src/dsp_tools/xmllib/models/dsp_base_resources.py", True),
            ("<string>", True),
            ("/Users/UserName/repoLocation/dsp-tools/test/unittests/xmllib/models/test_dsp_base_resources.py", False),
            ("/Users/UserName/repoLocation/dsp-tools/.venv/lib/python3.12/site-packages/_pytest/python.py", False),
            (
                ("/Users/UserName/Applications/PyCharm CE.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py"),
                False,
            ),
        ],
    )
    def test_filter_stack_frames(self, f_path, expected):
        assert _filter_stack_frames(f_path) == expected
