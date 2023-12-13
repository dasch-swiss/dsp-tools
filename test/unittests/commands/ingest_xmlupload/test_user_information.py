# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation


class TestIngestInformation:
    def test_no_problems(self) -> None:
        expected = (
            "All multimedia files referenced in the XML file were uploaded through dsp-ingest.\n"
            "No multimedia files were uploaded through dsp-ingest that were not referenced in the XML file."
        )
        assert IngestInformation([], []).all_good_msg() == expected

    def test_not_all_good(self) -> None:
        assert not IngestInformation(["unused_media"], []).all_good_msg()

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
            "    The file with the resource IDs and filenames was saved at './NotUploadedFilesToSipi.csv'.\n"
            "    The data XML file contains references to multimedia files "
            "which were not previously uploaded through dsp-ingest:\n"
            "    The file with the resource IDs and filenames was saved at './NotUploadedFilesToSipi.csv'."
        )
        res_info = IngestInformation(
            [
                "unused_media0",
                "unused_media1",
            ],
            [
                "no_up0",
                "no_up1",
            ],
            csv_filepath=Path(),
            maximum_prints=1,
        )._get_error_msg()
        assert res_info == expected


def test_unused_media_to_df() -> None:
    unused_media_list = [
        "unused_media0",
        "unused_media1",
    ]
    expected = pd.DataFrame({"Multimedia Filenames": unused_media_list})
    res_df = IngestInformation(unused_media_list, [], maximum_prints=1)._unused_media_to_df()
    assert_frame_equal(res_df, expected)


def test_unused_media_to_df_not_enough() -> None:
    assert not IngestInformation(["unused_media"], [], maximum_prints=1)._unused_media_to_df()


def test_no_uuid_to_df() -> None:
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
    )._no_uuid_to_df()
    assert_frame_equal(res_df, expected)


def test_no_uuid_to_df_not_enough() -> None:
    assert not IngestInformation([], [("ID_no_up0", "fileno_up0.jpg")])._unused_media_to_df()
