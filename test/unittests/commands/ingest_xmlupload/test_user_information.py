# pylint: disable=missing-class-docstring,missing-function-docstring

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation


class TestIngestInformation:
    def test_no_problems(self) -> None:
        expected = (
            "All media referenced in the XML file were uploaded to sipi.\n"
            "No media was uploaded to sipi that was not referenced in the XML file."
        )
        assert str(IngestInformation([], [])) == expected

    def test_unused_media(self) -> None:
        expected = "The following media were uploaded to sipi but not used in the data XML file:\n    - unused path"
        assert str(IngestInformation(["unused path"], [])) == expected

    def test_not_uploaded(self) -> None:
        expected = (
            "The following media were not uploaded to sipi but referenced in the data XML file:\n"
            "    - Resource ID: 'no upload id' | Filepath: 'media path'"
        )
        assert str(IngestInformation([], [("no upload id", "media path")])) == expected
