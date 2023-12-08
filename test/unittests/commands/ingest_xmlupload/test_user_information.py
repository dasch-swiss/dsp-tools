# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.ingest_xmlupload import user_information
from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation

user_information.csv_filepath = Path()
user_information.maximum_prints = 3


class TestIngestInformation:
    def test_no_problems(self) -> None:
        expected = (
            "All media referenced in the XML file were uploaded to sipi.\n"
            "No media was uploaded to sipi that was not referenced in the XML file."
        )
        assert IngestInformation([], []).all_good_msg() == expected

    def test_not_all_good(self) -> None:
        assert not IngestInformation(["unused_media"], []).all_good_msg()

    def test_unused_media(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the media referenced in the XML.\n"
            "    The following media were uploaded to sipi but not referenced in the data XML file:\n"
            "    - unused_media"
        )
        res_msg = IngestInformation(["unused_media"], [])._get_error_msg()
        assert res_msg == expected

    def test_not_uploaded(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the media referenced in the XML.\n"
            "    The following media were not uploaded to sipi but referenced in the data XML file:\n"
            "    - Resource ID: 'no upload id' | Filepath: 'media path'"
        )
        res_msg = IngestInformation([], [("no upload id", "media path")])._get_error_msg()
        assert res_msg == expected

    def test_all_problem_more_than_ten(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the media referenced in the XML.\n"
            "    Media was uploaded to Sipi which was not referenced in the XML file.\n"
            "    The file 'UnusedMediaUploadedInSipi.csv' was saved in '.' with the filenames.\n\n"
            "    Media was referenced in the XML file but not previously uploaded to sipi:\n"
            "    The file 'NotUploadedFilesToSipi.csv' was saved in '.' with the resource IDs and filenames."
        )
        res_msg = IngestInformation(
            [
                "unused_media0",
                "unused_media1",
                "unused_media2",
                "unused_media3",
            ],
            [
                "no_up0",
                "no_up1",
                "no_up2",
                "no_up3",
            ],
        )._get_error_msg()
        assert res_msg == expected


def test_unused_media_to_df() -> None:
    unused_media_list = [
        "unused_media0",
        "unused_media1",
        "unused_media2",
        "unused_media3",
    ]
    expected = pd.DataFrame({"Media Filenames": unused_media_list})
    res_df = IngestInformation(unused_media_list, [])._unused_media_to_df()
    assert_frame_equal(res_df, expected)


def test_unused_media_to_df_not_enough() -> None:
    assert not IngestInformation(["unused_media"], [])._unused_media_to_df()


def test_no_uuid_to_df() -> None:
    expected = pd.DataFrame(
        {
            "Resource ID": [
                "ID_no_up0",
                "ID_no_up1",
                "ID_no_up2",
                "ID_no_up3",
            ],
            "Filepath": [
                "fileno_up0.jpg",
                "fileno_up1.jpg",
                "fileno_up2.jpg",
                "fileno_up3.jpg",
            ],
        }
    )
    res_df = IngestInformation(
        [],
        [
            ("ID_no_up0", "fileno_up0.jpg"),
            ("ID_no_up1", "fileno_up1.jpg"),
            ("ID_no_up2", "fileno_up2.jpg"),
            ("ID_no_up3", "fileno_up3.jpg"),
        ],
    )._no_uuid_to_df()
    assert_frame_equal(res_df, expected)


def test_no_uuid_to_df_not_enough() -> None:
    assert not IngestInformation([], [("ID_no_up0", "fileno_up0.jpg")])._unused_media_to_df()
