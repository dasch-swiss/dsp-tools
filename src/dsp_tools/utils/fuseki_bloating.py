from dsp_tools.clients.fuseki_metrics import FusekiBloatingLevel
from dsp_tools.clients.fuseki_metrics import FusekiMetrics

_10_GB_IN_BYTES = 10_000_000_000
_20_GB_IN_BYTES = _10_GB_IN_BYTES * 2


def communicate_fuseki_bloating(fuseki_metrics: FusekiMetrics) -> None:
    pass


def _get_bloating_level(size_diff: int) -> FusekiBloatingLevel:
    pass


def _analyse_fuseki_sizes(fuseki_metrics: FusekiMetrics) -> int | None:
    pass
