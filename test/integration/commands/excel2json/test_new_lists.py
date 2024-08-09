from pathlib import Path
from typing import Any

import pytest

from dsp_tools.commands.excel2json.new_lists import new_excel2lists


@pytest.fixture()
def list_correct() -> list[dict[str, Any]]:
    list_dict, _ = new_excel2lists(Path("testdata/excel2json/new_excel2json_files/lists"))
    return list_dict


if __name__ == "__main__":
    pytest.main([__file__])
