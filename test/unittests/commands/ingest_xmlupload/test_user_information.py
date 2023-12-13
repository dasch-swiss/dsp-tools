# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation


class TestIngestInformation:
    def test_no_problems(self) -> None:
        expected = (
            "All multimedia files referenced in the XML file were uploaded to sipi.\n"
            "No multimedia files was uploaded to sipi that was not referenced in the XML file."
        )
        assert IngestInformation([], []).all_good_msg() == expected

    def test_not_all_good(self) -> None:
        assert not IngestInformation(["unused_media"], []).all_good_msg()

    def test_unused_media(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    The following multimedia files were uploaded to sipi but not referenced in the data XML file:\n"
            "    - unused_media"
        )
        res_info = IngestInformation(["unused_media"], [])._get_error_msg()
        assert res_info == expected

    def test_not_uploaded(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    The following multimedia files were not uploaded to sipi but referenced in the data XML file:\n"
            "    - Resource ID: 'no upload id' | Filepath: 'media path'"
        )
        res_info = IngestInformation([], [("no upload id", "media path")])._get_error_msg()
        assert res_info == expected

    def test_all_problem_with_df_msg(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
            "    Multimedia files was uploaded to Sipi which was not referenced in the XML file.\n"
            "    The file 'UnusedMediaUploadedInSipi.csv' was saved in '.' with the filenames.\n\n"
            "    Multimedia files was referenced in the XML file but not previously uploaded to sipi:\n"
            "    The file 'NotUploadedFilesToSipi.csv' was saved in '.' with the resource IDs and filenames."
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
