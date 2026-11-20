from dsp_tools.error.exceptions import ANY_DSP_ERROR
from dsp_tools.error.exceptions import ANY_USER_ERROR
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import UserError
from dsp_vre_lib.clients.exceptions import DspVreLibBaseError
from dsp_vre_lib.clients.exceptions import DspVreLibUserError


def test_any_dsp_error_contains_both_roots() -> None:
    assert set(ANY_DSP_ERROR) == {BaseError, DspVreLibBaseError}


def test_any_user_error_contains_both_user_roots() -> None:
    assert set(ANY_USER_ERROR) == {UserError, DspVreLibUserError}
