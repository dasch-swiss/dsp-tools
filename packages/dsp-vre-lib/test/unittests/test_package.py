from importlib.metadata import version
from pathlib import Path

import dsp_vre_lib


def test_distribution_is_installed() -> None:
    assert version("dsp-vre-lib")


def test_package_is_typed() -> None:
    assert (Path(dsp_vre_lib.__file__).parent / "py.typed").is_file()
