from typing import Any

import pandas as pd
import pytest

from dsp_tools.xmllib.value_converters import convert_to_bool_string


@pytest.mark.parametrize("val", ["false", "0  ", "  0.0", "NO", False])
def test_convert_to_bool_false(val: Any) -> None:
    assert convert_to_bool_string(val) == "false"


@pytest.mark.parametrize("val", ["TRUE ", "  1", "1.0", "Yes", True])
def test_convert_to_bool_true(val: Any) -> None:
    assert convert_to_bool_string(val) == "true"


@pytest.mark.parametrize("val", [pd.NA, None, 2.421, 10, "other", "  "])
def test_convert_to_bool_failure(val: Any) -> None:
    assert convert_to_bool_string(val) == str(val)


if __name__ == "__main__":
    pytest.main([__file__])
