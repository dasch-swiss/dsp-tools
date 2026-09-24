from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.validation.python_checks import check_geolocation_values
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedGeolocation
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_LOCATION = f"{ONTO}hasLocation"
CLASS = f"{ONTO}Class"


def _resource(res_id: str, *geolocations: ParsedGeolocation) -> ParsedResource:
    values = [
        ParsedValue(HAS_LOCATION, geo, KnoraValueType.GEOLOCATION_VALUE, None, None, None, i)
        for i, geo in enumerate(geolocations)
    ]
    return ParsedResource(res_id, CLASS, "label", None, values, None, None)


def test_valid_values_have_no_problems() -> None:
    resources = [
        _resource("crs84", ParsedGeolocation("CRS84", {"longitude": "8.55", "latitude": "47.37"})),
        _resource("lv95", ParsedGeolocation("LV95", {"easting": "2600000", "northing": "1200000"})),
        ParsedResource(
            "other",
            CLASS,
            "label",
            None,
            [ParsedValue(HAS_LOCATION, "text", KnoraValueType.SIMPLETEXT_VALUE, None, None, None, 0)],
            None,
            None,
        ),
    ]
    assert not check_geolocation_values(resources)


def test_out_of_range_names_the_attribute_its_range_and_its_crs() -> None:
    resources = [_resource("res", ParsedGeolocation("LV03", {"easting": "2600000", "northing": "200000"}))]
    problems = check_geolocation_values(resources)
    assert len(problems) == 1
    problem = problems.pop(0)
    assert problem.problem_type == ProblemType.GENERIC
    assert problem.severity == Severity.VIOLATION
    assert problem.res_id == "res"
    assert problem.res_type == "onto:Class"
    assert problem.prop_name == "onto:hasLocation"
    assert problem.message == (
        "The easting '2600000' is outside the valid range for Swiss LV03: 484273.3 to 837939.88 inclusive."
    )
    assert problem.input_value == 'crs="LV03" easting="2600000" northing="200000"'


def test_wrong_pair_and_missing_ordinate_are_each_reported() -> None:
    resources = [
        _resource(
            "res",
            ParsedGeolocation("LV95", {"longitude": "8.55", "latitude": "47.37"}),
            ParsedGeolocation("CRS84", {"longitude": "8.55"}),
        )
    ]
    problems = check_geolocation_values(resources)
    assert len(problems) == 2
    wrong_pair, missing = problems
    assert wrong_pair.message is not None
    assert "expected the attributes 'easting' and 'northing'" in wrong_pair.message
    assert missing.message is not None
    assert "'latitude' is missing" in missing.message
