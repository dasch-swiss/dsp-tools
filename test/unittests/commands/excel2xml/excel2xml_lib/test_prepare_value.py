import unittest
from typing import Union

import numpy as np
import pandas as pd
import pytest

from dsp_tools import excel2xml

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestPrepareValue(unittest.TestCase):
    def test_prepare_value(self) -> None:
        identical_values = ["Test", "Test", "Test"]
        different_values: list[Union[str, int, float]] = [1, 1.0, "1", "1.0", " 1 "]
        values_with_nas: list[Union[str, int, float]] = ["test", "", 1, np.nan, pd.NA, 0]  # type: ignore[list-item]

        for val in different_values:
            values_output = excel2xml.prepare_value(val)
            self.assertEqual([x.value for x in values_output], [val])

            values_output = excel2xml.prepare_value(excel2xml.PropertyElement(val))
            self.assertEqual([x.value for x in values_output], [val])

        values_output = excel2xml.prepare_value(identical_values)
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in identical_values])
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = excel2xml.prepare_value(different_values)
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in different_values])
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = excel2xml.prepare_value(values_with_nas)
        self.assertEqual([x.value for x in values_output], values_with_nas)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in values_with_nas])
        self.assertEqual([x.value for x in values_output], values_with_nas)


if __name__ == "__main__":
    pytest.main([__file__])
