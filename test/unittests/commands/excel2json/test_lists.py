import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json.new_lists import _get_preferred_language_for_id
from dsp_tools.models.exceptions import InputError


class TestGetPreferredLanguageForId:
    def test_get_preferred_language_for_id_en(self) -> None:
        columns = pd.Series(["en_1", "de_2", "fr_3", "it_4", "rm_5"])
        assert _get_preferred_language_for_id(columns) == "en"

    def test_get_preferred_language_for_id_de(self) -> None:
        columns = pd.Series(["de_1", "fr_2", "it_3", "rm_4"])
        assert _get_preferred_language_for_id(columns) == "de"

    def test_get_preferred_language_for_id_fr(self) -> None:
        columns = pd.Series(["fr_1", "it_2", "rm_3"])
        assert _get_preferred_language_for_id(columns) == "fr"

    def test_get_preferred_language_for_id_it(self) -> None:
        columns = pd.Series(["it_1", "rm_2"])
        assert _get_preferred_language_for_id(columns) == "it"

    def test_get_preferred_language_for_id_rm(self) -> None:
        columns = pd.Series(["rm_1"])
        assert _get_preferred_language_for_id(columns) == "rm"

    def test_get_preferred_language_for_id_raises(self) -> None:
        columns = pd.Series(["es_6"])
        msg = regex.escape(
            "The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n" "The columns are: es_6"
        )
        with pytest.raises(InputError, match=msg):
            _get_preferred_language_for_id(columns)


if __name__ == "__main__":
    pytest.main([__file__])
