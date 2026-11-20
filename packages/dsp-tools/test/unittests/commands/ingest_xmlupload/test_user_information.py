from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.ingest_xmlupload.create_resources.user_information import IngestInformation


class TestIngestInformation:
    def test_no_problems(self) -> None:
        expected = (
            "All multimedia files referenced in the XML file were uploaded through dsp-ingest.\n"
            "All multimedia files uploaded through dsp-ingest were referenced in the XML file."
        )
        assert IngestInformation([], []).ok_msg() == expected

    def test_not_all_good(self) -> None:
        assert not IngestInformation(["unused_media"], []).ok_msg()

    def test_unused_media(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    The data XML file does not reference the following multimedia files "
            "which were previously uploaded through dsp-ingest:\n"
            "    - unused_media"
        )
        res_info = IngestInformation(["unused_media"], [])._get_error_msg()
        assert res_info == expected

    def test_not_uploaded(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    The data XML file contains references to the following multimedia files "
            "which were not previously uploaded through dsp-ingest:\n"
            "    - Resource ID: 'no upload id' | Filepath: 'media path'"
        )
        res_info = IngestInformation([], [("no upload id", "media path")])._get_error_msg()
        assert res_info == expected

    def test_all_problem_with_df_msg(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    The data XML file does not reference all the multimedia files "
            "which were previously uploaded through dsp-ingest.\n"
            "    The file with the unused filenames was saved at 'UnusedMediaUploaded.csv'.\n"
            "    The data XML file contains references to multimedia files "
            "which were not previously uploaded through dsp-ingest:\n"
            "    The file with the resource IDs and problematic filenames was saved at 'FilesNotUploaded.csv'."
        )
        res_info = IngestInformation(
            [
                "unused_media0",
                "unused_media1",
            ],
            [
                ("no_up0_id", "no_up0_file"),
                ("no_up1_id", "no_up1_file"),
            ],
            csv_directory_path=Path(),
            maximum_prints=1,
        )._get_error_msg()
        assert res_info == expected


def test_unused_media_to_df() -> None:
    unused_media_list = [
        "unused_media0",
        "unused_media1",
    ]
    expected = pd.DataFrame({"Multimedia Filenames": unused_media_list})
    res_df = IngestInformation(unused_media_list, [], maximum_prints=1)._unused_mediafiles_to_df()
    assert res_df is not None
    assert_frame_equal(res_df, expected)


def test_unused_media_to_df_not_enough() -> None:
    assert not IngestInformation(["unused_media"], [], maximum_prints=1)._unused_mediafiles_to_df()


def test_no_id_to_df() -> None:
    expected = pd.DataFrame(
        {
            "Resource ID": [
                "ID_no_up0",
                "ID_no_up1",
            ],
            "Filepath": [
                "fileno_up0.jpg",
                "fileno_up1.jpg",
            ],
        }
    )
    res_df = IngestInformation(
        [],
        [
            ("ID_no_up0", "fileno_up0.jpg"),
            ("ID_no_up1", "fileno_up1.jpg"),
        ],
        maximum_prints=1,
    )._mediafiles_no_id_to_df()
    assert res_df is not None
    assert_frame_equal(res_df, expected)


def test_no_id_to_df_not_enough() -> None:
    assert not IngestInformation([], [("ID_no_up0", "fileno_up0.jpg")])._unused_mediafiles_to_df()


if __name__ == "__main__":
    pytest.main([__file__])
