"""unit tests for date values"""

# pylint: disable=protected-access,missing-class-docstring,missing-function-docstring

import unittest

import pytest

from dsp_tools.models.helpers import Actions
from dsp_tools.models.value import DateValue


class TestValue(unittest.TestCase):

    def test_date_value(self) -> None:
        date: DateValue = DateValue("JULIAN:BCE:0700:BCE:0600")
        self.assertEqual(date._calendar, 'JULIAN')

        self.assertEqual(date._e1, 'BCE')
        self.assertEqual(date._y1, 700)
        self.assertEqual(date._m1, None)
        self.assertEqual(date._d1, None)

        self.assertEqual(date._e2, 'BCE')
        self.assertEqual(date._y2, 600)
        self.assertEqual(date._m2, None)
        self.assertEqual(date._d2, None)

        json_ld = date.toJsonLdObj(Actions.Create)

        self.assertEqual(json_ld['knora-api:dateValueHasCalendar'], 'JULIAN')
        self.assertEqual(json_ld['knora-api:dateValueHasStartEra'], 'BCE')
        self.assertEqual(json_ld['knora-api:dateValueHasStartYear'], 700)
        self.assertEqual(json_ld['knora-api:dateValueHasEndYear'], 600)
        self.assertEqual(json_ld['knora-api:dateValueHasEndEra'], 'BCE')


if __name__ == "__main__":
    pytest.main([__file__])
