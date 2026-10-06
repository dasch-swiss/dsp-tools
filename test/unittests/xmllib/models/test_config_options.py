from dsp_tools.utils.geolocation_constants import CRS_BY_CODE
from dsp_tools.xmllib.models.config_options import CoordinateSystem


def test_coordinate_system_has_one_member_per_supported_crs() -> None:
    assert {member.value for member in CoordinateSystem} == set(CRS_BY_CODE)


def test_coordinate_system_member_names_state_the_crs_kind() -> None:
    for member in CoordinateSystem:
        assert member.name == f"{CRS_BY_CODE[member.value].kind.upper()}_{member.value}"
