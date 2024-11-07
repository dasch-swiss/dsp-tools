from typing import Any

import pandas as pd
import pytest

from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.value_converters import convert_to_bool_string
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


@pytest.mark.parametrize("val", ["false", "0  ", "  0.0", "NO", False, "non", "nein"])
def test_convert_to_bool_false(val: Any) -> None:
    assert convert_to_bool_string(val) == "false"


@pytest.mark.parametrize("val", ["TRUE ", "  1", "1.0", "Yes", True, "ouI", "JA"])
def test_convert_to_bool_true(val: Any) -> None:
    assert convert_to_bool_string(val) == "true"


@pytest.mark.parametrize("val", [pd.NA, None, 2.421, 10, "other", "  "])
def test_convert_to_bool_failure(val: Any) -> None:
    assert convert_to_bool_string(val) == str(val)


def test_replace_newlines_with_tags_none() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.NONE)
    assert result == text


def test_replace_newlines_with_tags_newline() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.LINEBREAK)
    assert result == "Start<br/>Middle<br/><br/>Final"


def test_replace_newlines_with_tags_paragraph() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.PARAGRAPH)
    assert result == "<p>Start</p><p>Middle</p><p>Final</p>"


if __name__ == "__main__":
    pytest.main([__file__])
