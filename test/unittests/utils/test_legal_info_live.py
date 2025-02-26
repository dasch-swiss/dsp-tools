# mypy: disable-error-code="method-assign"

from dsp_tools.utils.legal_info_client_live import _segment_data


def test_segment_data_more_than_limit():
    data_list = [str(x) for x in range(203)]
    result = _segment_data(data_list)
    assert len(result) == 3
    assert result[0][0] == "0"
    assert result[0][-1] == "99"
    assert result[1][0] == "100"
    assert result[1][-1] == "199"
    assert result[2][0] == "200"
    assert result[2][-1] == "202"


def test_segment_data_less_than_limit():
    data_list = [str(x) for x in range(4)]
    result = _segment_data(data_list)
    assert len(result) == 1
    assert len(result[0]) == 4
