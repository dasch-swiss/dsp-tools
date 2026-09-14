from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from loguru import logger

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError


@pytest.fixture
def raise_already_logged_docker_failure() -> Callable[..., None]:
    def _raise(*_args: object, **_kwargs: object) -> None:
        # simulates ShaclCliValidator.validate() itself: logs once at the origin, then raises
        logger.exception("Docker command failed with 1: stdout='stdout', stderr='stderr'")
        raise ShaclValidationCliError(1, "stdout", "stderr")

    return _raise


@pytest.fixture
def patch_temp_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Callable[[str], None]:
    def _patch(target: str) -> None:
        # narrowly scoped to the calling module's imported name, instead of monkeypatching the
        # global pathlib.Path.home() that get_temp_directory() would otherwise call
        monkeypatch.setattr(target, lambda: TemporaryDirectory(dir=tmp_path))

    return _patch
