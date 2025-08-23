from pathlib import Path
from typing import Any
from typing import TypeVar

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib import XMLRoot
from dsp_tools.xmllib.models.internal.values import BooleanValue
from dsp_tools.xmllib.models.internal.values import ColorValue
from dsp_tools.xmllib.models.internal.values import DateValue
from dsp_tools.xmllib.models.internal.values import DecimalValue
from dsp_tools.xmllib.models.internal.values import GeonameValue
from dsp_tools.xmllib.models.internal.values import IntValue
from dsp_tools.xmllib.models.internal.values import LinkValue
from dsp_tools.xmllib.models.internal.values import ListValue
from dsp_tools.xmllib.models.internal.values import Richtext
from dsp_tools.xmllib.models.internal.values import SimpleText
from dsp_tools.xmllib.models.internal.values import TimeValue
from dsp_tools.xmllib.models.internal.values import UriValue
from dsp_tools.xmllib.models.internal.values import Value

T = TypeVar("T", bound=Value)

# This is to be used with the ontology: testdata/validate-data/generic/project.json


def _create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def _add_boolean(res: Resource, number_of_vals: int) -> Resource:
    prop_names = [f":testBoolean{i}" for i in range(1, number_of_vals + 1)]
    bools = [BooleanValue("true", x) for x in prop_names]
    res.values.extend(bools)
    return res


def _add_color(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testColor", "#00ff00", ColorValue, number_of_vals)


def _add_date(res: Resource, number_of_vals: int) -> Resource:
    return _add_values(res, ":testDate", "GREGORIAN:AD:0476-09-04:AD:0476-09-04", DateValue, number_of_vals)


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


def _add_link(res: Resource, number_of_vals: int) -> Resource:
    content = [f"target_{i}" for i in range(number_of_vals)]
    vals = [LinkValue(x, ":testHasLinkTo") for x in content]
    res.values.extend(vals)
    return res


def _create_link_target_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"target_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


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


def _add_values(res: Resource, prop: str, val: Any, func: type[T], number_of_vals: int) -> Resource:
    vals = [_create_one_value(prop, val, func) for _ in range(number_of_vals)]
    res.values.extend(vals)
    return res


def _create_one_value(prop: str, val: Any, func: type[T]) -> T:
    return func(val, prop)


if __name__ == "__main__":

    def create_every_type(number_of_res: int, number_of_vals: int = 13) -> None:
        file_p = Path("x_fuseki_bloating_files/value_types")
        file_p.mkdir(exist_ok=True, parents=True)

        funcs = [
            (_add_boolean, "boolean"),
            (_add_color, "color"),
            (_add_date, "date"),
            (_add_decimal, "decimal"),
            (_add_geoname, "geoname"),
            (_add_int, "int"),
            (_add_list, "list"),
            (_add_richtext, "richtext"),
            (_add_textarea, "textarea"),
            (_add_simpletext, "simpletext"),
            (_add_time, "time"),
            (_add_uri, "uri"),
        ]

        for f, name in funcs:
            root = XMLRoot.create_new("9999", "onto")
            resources = [_create_one_resource(x) for x in range(number_of_res)]
            added = [f(r, number_of_vals) for r in resources]
            root.add_resource_multiple(added)
            xml_name = f"res-{number_of_res}_val-{number_of_vals}_{name}.xml"
            root.write_file(file_p / xml_name)

        # link value needs target resources
        link_root = XMLRoot.create_new("9999", "onto")
        resources = [_create_one_resource(x) for x in range(number_of_res)]
        added = [_add_link(r, number_of_vals) for r in resources]
        target_res = [_create_link_target_resource(i) for i in range(number_of_vals)]
        link_root.add_resource_multiple(target_res)
        link_root.add_resource_multiple(added)
        xml_name = f"res-{number_of_res}_val-{number_of_vals}_link.xml"
        link_root.write_file(file_p / xml_name)

        # every type once
        every_type_root = XMLRoot.create_new("9999", "onto")
        resources = [_create_one_resource(x) for x in range(number_of_res)]
        every_type_root.add_resource(_create_link_target_resource(0))
        # Add one of each value type to each resource
        for res in resources:
            _add_boolean(res, 1)
            _add_color(res, 1)
            _add_date(res, 1)
            _add_decimal(res, 1)
            _add_geoname(res, 1)
            _add_int(res, 1)
            _add_list(res, 1)
            _add_richtext(res, 1)
            _add_textarea(res, 1)
            _add_simpletext(res, 1)
            _add_time(res, 1)
            _add_uri(res, 1)
            _add_link(res, 1)
        every_type_root.add_resource_multiple(resources)
        xml_name = f"res-{number_of_res}_val-13_every_type.xml"
        every_type_root.write_file(file_p / xml_name)

    create_every_type(10_000)
