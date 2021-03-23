import unittest
from pprint import pprint
from knora.dsplib.models.value import DateValue
from knora.dsplib.models.helpers import Actions

class TestValue(unittest.TestCase):

    def test_date_value(self):
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

        jsonLD = date.toJsonLdObj(Actions.Create)

        self.assertEqual(jsonLD['knora-api:dateValueHasCalendar'], 'JULIAN')
        self.assertEqual(jsonLD['knora-api:dateValueHasStartEra'], 'BCE')
        self.assertEqual(jsonLD['knora-api:dateValueHasStartYear'], 700)
        self.assertEqual(jsonLD['knora-api:dateValueHasEndYear'], 600)
        self.assertEqual(jsonLD['knora-api:dateValueHasEndEra'], 'BCE')


if __name__ == '__main__':
    unittest.main()
