from collections.abc import Callable
from typing import Any

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib.models.internal.values import BooleanValue
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import DateValue
from dsp_tools.xmllib.models.internal.values import DecimalValue
from dsp_tools.xmllib.models.internal.values import GeonameValue
from dsp_tools.xmllib.models.internal.values import IntValue
from dsp_tools.xmllib.models.internal.values import ListValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.models.internal.values import SimpleText
from dsp_tools.xmllib.models.internal.values import TimeValue
from dsp_tools.xmllib.models.internal.values import UriValue
from dsp_tools.xmllib.models.internal.values import Value

# This is to be used with the ontology: testdata/validate-data/generic/project.json


def create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _add_boolean(res: Resource, number_of_vals: int) -> Resource:
    prop_names = [f":testBoolean{i}" for i in range(1, number_of_vals + 1)]
    bools = [BooleanValue("true", x) for x in prop_names]
    res.values.extend(bools)
    return res


def _add_color(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testColor", "#00ff00", ColorValue, number_of_vals)


def _add_date(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testSuperDate", "GREGORIAN:AD:0476-09-04:AD:0476-09-04", DateValue, number_of_vals)


def _add_decimal(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testDecimalSimpleText", "1.1", DecimalValue, number_of_vals)


def _add_geoname(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testGeoname", "1111111", GeonameValue, number_of_vals)


def _add_int(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testIntegerSimpleText", "1", IntValue, number_of_vals)


def _add_list(res: Resource, number_of_vals: int) -> Resource:
    vals = [ListValue("n1", "firstList", ":testListProp") for _ in range(number_of_vals)]
    res.values.extend(vals)
    return res


# TODO: Link Value
def _add_(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":", "", BooleanValue, number_of_vals)


def _add_richtext(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testRichtext", "<p>Text</p>", Richtext, number_of_vals)


def _add_textarea(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testTextarea", "Text", SimpleText, number_of_vals)


def _add_simpletext(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testSimpleText", "Text", SimpleText, number_of_vals)


def _add_time(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testTimeValue", "2019-10-23T13:45:12.01-14:00", TimeValue, number_of_vals)


def _add_uri(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testUriValue", "https://dasch.swiss", UriValue, number_of_vals)


def _add_values(res: Resource, prop: str, val: Any, func: Callable[Any, str], number_of_vals: int) -> Resource:
    vals = [_create_one_value(prop, val, func) for _ in range(number_of_vals)]
    res.values.extend(vals)
    return res


def _create_one_value(prop: str, val: Any, func: Callable[Any, str]) -> Value:
    return func(val, prop)
