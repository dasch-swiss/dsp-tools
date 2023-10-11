# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access


import pytest
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.create_graph import _calculate_weight_links, _create_weighted_dict


def test_create_weighted_dict() -> None:
    test_dict = {"A": ["B", "C"], "B": ["A", "A", "C", "D"], "D": ["C"]}
    res = _create_weighted_dict(test_dict)
    expected = {"A": [{"B": 1}, {"C": 1}], "B": [{"A": 2}, {"D": 1}, {"C": 1}], "D": [{"C": 1}]}
    assert list(expected.keys()) == unordered(list(res.keys()))
    for k_expected, v_expected in expected.items():
        assert v_expected == unordered(res[k_expected])


def test_calculate_weight_links_one() -> None:
    test_list = ["B", "C"]
    expected = [{"B": 1}, {"C": 1}]
    res = _calculate_weight_links(test_list)
    assert expected == unordered(res)


def test_calculate_weight_links_two() -> None:
    test_list = ["A", "A", "C", "D"]
    expected = [{"A": 2}, {"D": 1}, {"C": 1}]
    res = _calculate_weight_links(test_list)
    assert expected == unordered(res)


def test_calculate_weight_links_three() -> None:
    test_list = ["C"]
    expected = [{"C": 1}]
    res = _calculate_weight_links(test_list)
    assert expected == unordered(res)


if __name__ == "__main__":
    pytest.main([__file__])
