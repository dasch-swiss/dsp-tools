from typing import Any

import pytest

from dsp_tools.commands.xml_validate.deserialise_api_responses import _deserialise_one_list


def test_deserialise_lists(list_from_api: dict[str, Any]) -> None:
    res = _deserialise_one_list(list_from_api)
    assert res.list_name == "onlyList"
    assert set(res.nodes) == {"n1", "n1.1", "n1.1.1"}


if __name__ == "__main__":
    pytest.main([__file__])
