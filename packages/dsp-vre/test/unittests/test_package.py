from importlib.metadata import version
from pathlib import Path

import dsp_vre


def test_distribution_is_installed() -> None:
    assert version("dsp-vre")


def test_package_is_typed() -> None:
    assert (Path(dsp_vre.__file__).parent / "py.typed").is_file()
