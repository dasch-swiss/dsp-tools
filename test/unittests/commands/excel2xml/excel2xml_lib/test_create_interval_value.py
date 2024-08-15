import pytest

from dsp_tools.commands.excel2xml.excel2xml_lib import create_interval_value


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("0:00:00.1", "0:00:02.345", "0.1:2.345"),
        ("00:00:00", "00:00:01", "0:1"),
        ("00:00:00", "01:00:00", "0:3600"),
        ("01:00:00", "01:00:00", "3600:3600"),
        ("01:30:00", "02:45:00", "5400:9900"),
        ("23:59:58", "23:59:59", "86398:86399"),
    ],
)
def test_create_interval_value_happy_path(start: str, end: str, expected: str) -> None:
    result = create_interval_value(start, end)
    assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("01:00", "02:00"),
        ("24:00:00", "23:59:59"),
        ("00:60:00", "02:00:00"),
        ("01:00:00", "02:60:00"),
        ("00:00:60", "01:00:00"),
        ("01:00:00", "02:00:60"),
        ("not:time", "01:00:00"),
        ("01:00:00", "not:time"),
    ],
)
def test_create_interval_value_error_cases(start: str, end: str) -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        create_interval_value(start, end)
