from dsp_tools.xmllib.models.provenance import SourceProvenance


class TestSourceProvenance:
    def test_only_source_file_required(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx")
        assert prov.source_file == "data.xlsx"
        assert prov.sheet is None
        assert prov.row is None
        assert prov.cell is None

    def test_all_fields(self) -> None:
        prov = SourceProvenance(source_file="data.xlsx", sheet="Sheet1", row=5, cell="C")
        assert prov.source_file == "data.xlsx"
        assert prov.sheet == "Sheet1"
        assert prov.row == 5
        assert prov.cell == "C"
