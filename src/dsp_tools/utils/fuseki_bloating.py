from typing import assert_never

from loguru import logger

from dsp_tools.clients.fuseki_metrics import FusekiBloatingLevel
from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.config.logger_config import LOGGER_SAVEPATH
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.utils.ansi_colors import BOLD_YELLOW
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT

_1_GB_IN_BYTES = 1_000_000_000
WARNING_BLOATING = 10 * _1_GB_IN_BYTES
CRITICAL_BLOATING = 20 * _1_GB_IN_BYTES


def communicate_fuseki_bloating(fuseki_metrics: FusekiMetrics) -> None:
    size_diff = _analyse_fuseki_sizes(fuseki_metrics)
    bloating_level = _get_bloating_level(size_diff)
    if size_diff is not None:
        rounded = round(size_diff / _1_GB_IN_BYTES, 2)
    else:
        rounded = None
    msg = (
        f"The xmlupload caused the database to use {rounded} GB disk space. "
        f"Please check that your test server has enough disk space for an upload. "
        f"If you have any questions contact the dsp-tools developers at info@dasch.swiss."
    )
    match bloating_level:
        case FusekiBloatingLevel.OK:
            logger.debug(msg)
        case FusekiBloatingLevel.WARNING:
            logger.warning(msg)
            print(f"{BOLD_YELLOW}WARNING: {msg}{RESET_TO_DEFAULT}")
        case FusekiBloatingLevel.CRITICAL:
            logger.warning(msg)
            print(f"{BACKGROUND_BOLD_RED}WARNING: {msg}{RESET_TO_DEFAULT}")
        case FusekiBloatingLevel.CALCULATION_FAILURE:
            msg = (
                "The database bloating size could not be calculated. "
                f"Please contact the dsp-tools developers (at info@dasch.swiss) "
                f"with your logs saved at {LOGGER_SAVEPATH}."
            )
            print(f"{BACKGROUND_BOLD_RED}{msg}{RESET_TO_DEFAULT}")
            logger.error(msg)
        case _:
            assert_never(bloating_level)


def _get_bloating_level(size_diff: int | None) -> FusekiBloatingLevel:
    if size_diff is None:
        return FusekiBloatingLevel.CALCULATION_FAILURE
    if size_diff <= WARNING_BLOATING:
        return FusekiBloatingLevel.OK
    if size_diff <= CRITICAL_BLOATING:
        return FusekiBloatingLevel.WARNING
    return FusekiBloatingLevel.CRITICAL


def _analyse_fuseki_sizes(fuseki_metrics: FusekiMetrics) -> int | None:
    if fuseki_metrics.end_size is not None and fuseki_metrics.start_size is not None:
        return fuseki_metrics.end_size - fuseki_metrics.start_size
    return None
