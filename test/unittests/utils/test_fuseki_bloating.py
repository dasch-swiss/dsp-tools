from dsp_tools.clients.fuseki_metrics import FusekiBloatingLevel
from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.utils.fuseki_bloating import CRITICAL_BLOATING
from dsp_tools.utils.fuseki_bloating import WARNING_BLOATING
from dsp_tools.utils.fuseki_bloating import _analyse_fuseki_sizes
from dsp_tools.utils.fuseki_bloating import _get_bloating_level


class TestAnalyseFusekiSizes:
    def test_both_sizes_present_returns_difference(self) -> None:
        fuseki_metrics = FusekiMetrics(size_before=1000, size_after=2000)
        result = _analyse_fuseki_sizes(fuseki_metrics)
        assert result == 1000

    def test_size_before_none_returns_none(self) -> None:
        fuseki_metrics = FusekiMetrics(size_before=None, size_after=2000)
        result = _analyse_fuseki_sizes(fuseki_metrics)
        assert result is None

    def test_size_after_none_returns_none(self) -> None:
        fuseki_metrics = FusekiMetrics(size_before=1000, size_after=None)
        result = _analyse_fuseki_sizes(fuseki_metrics)
        assert result is None

    def test_both_sizes_none_returns_none(self) -> None:
        fuseki_metrics = FusekiMetrics(size_before=None, size_after=None)
        result = _analyse_fuseki_sizes(fuseki_metrics)
        assert result is None


class TestGetBloatingLevel:
    def test_none_input_returns_calculation_failure(self) -> None:
        result = _get_bloating_level(None)
        assert result == FusekiBloatingLevel.CALCULATION_FAILURE

    def test_small_size_returns_non_critical(self) -> None:
        result = _get_bloating_level(WARNING_BLOATING - 1000)
        assert result == FusekiBloatingLevel.NON_CRITICAL

    def test_exactly_warning_threshold_returns_warning(self) -> None:
        result = _get_bloating_level(WARNING_BLOATING + 1)
        assert result == FusekiBloatingLevel.WARNING

    def test_exactly_critical_threshold_returns_critical(self) -> None:
        result = _get_bloating_level(CRITICAL_BLOATING + 1)
        assert result == FusekiBloatingLevel.CRITICAL
