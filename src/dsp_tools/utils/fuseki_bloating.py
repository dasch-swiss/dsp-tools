from typing import assert_never

from loguru import logger

from dsp_tools.clients.fuseki_metrics import FusekiBloatingLevel
from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.utils.ansi_colors import BOLD_YELLOW
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT

_1_GB_IN_BYTES = 1_000_000_000
_WARNING_BLOATING = 10 * _1_GB_IN_BYTES
_CRITICAL_BLOATING = 20 * _1_GB_IN_BYTES


def communicate_fuseki_bloating(fuseki_metrics: FusekiMetrics) -> None:
    size_diff = _analyse_fuseki_sizes(fuseki_metrics)
    bloating_level = _get_bloating_level(size_diff)
    rounded = round(size_diff / _1_GB_IN_BYTES, 2)
    msg = (
        f"The xmlupload caused the database to use {rounded} GB memory. "
        f"Please check that your test server has enough memory for an upload. "
        f"If you have any questions contact the dsp-tools developers."
    )
    match bloating_level:
        case FusekiBloatingLevel.NON_CRITICAL:
            logger.debug(msg)
        case FusekiBloatingLevel.WARNING:
            logger.warning(msg)
            print(f"{BOLD_YELLOW}WARNING: {msg}{RESET_TO_DEFAULT}")
        case FusekiBloatingLevel.CRITICAL:
            print(f"{BACKGROUND_BOLD_RED}WARNING: {msg}{RESET_TO_DEFAULT}")
        case FusekiBloatingLevel.CALCULATION_FAILURE:
            msg = (
                "The database bloating size could not be calculated. "
                "Please contact the dsp-tools developers with your logs."
            )
            logger.error(msg)
            print(f"{BACKGROUND_BOLD_RED}{msg}{RESET_TO_DEFAULT}")
        case _:
            assert_never(bloating_level)


def _get_bloating_level(size_diff: int | None) -> FusekiBloatingLevel:
    if not size_diff:
        return FusekiBloatingLevel.CALCULATION_FAILURE
    if size_diff < _WARNING_BLOATING:
        return FusekiBloatingLevel.NON_CRITICAL
    if size_diff < _CRITICAL_BLOATING:
        return FusekiBloatingLevel.WARNING
    return FusekiBloatingLevel.CRITICAL


def _analyse_fuseki_sizes(fuseki_metrics: FusekiMetrics) -> int | None:
    all_there = True if fuseki_metrics.size_after is not None and fuseki_metrics.size_before is not None else False
    if not all_there:
        return None
    return fuseki_metrics.size_after - fuseki_metrics.size_before
