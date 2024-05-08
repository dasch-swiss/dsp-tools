import pytest

from dsp_tools.commands.xmlupload.resource_create_client import _to_boolean
from dsp_tools.models.exceptions import BaseError


def test_to_boolean() -> None:
    assert _to_boolean("true")
    assert _to_boolean("True")
    assert _to_boolean("1")
    assert _to_boolean(1)
    assert _to_boolean(True)
    assert not _to_boolean("false")
    assert not _to_boolean("False")
    assert not _to_boolean("0")
    assert not _to_boolean(0)
    assert not _to_boolean(False)
    with pytest.raises(BaseError):
        _to_boolean("foo")
    with pytest.raises(BaseError):
        _to_boolean(2)


if __name__ == "__main__":
    pytest.main([__file__])
