# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation


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
        res_msg = IngestInformation(["unused_media"], [])._get_error_msg(Path(), "", "")
        assert res_msg == expected

    def test_not_uploaded(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the media referenced in the XML.\n"
            "    The following media were not uploaded to sipi but referenced in the data XML file:\n"
            "    - Resource ID: 'no upload id' | Filepath: 'media path'"
        )
        res_msg = IngestInformation([], [("no upload id", "media path")])._get_error_msg(Path(), "", "")
        assert res_msg == expected

    def test_all_problem_more_than_ten(self) -> None:
        expected = (
            "The upload cannot continue as there are problems with the media referenced in the XML.\n"
            "    Media was uploaded to Sipi which was not referenced in the XML file.\n"
            "    The file 'unused_media.csv' was saved in '.' with the filenames.\n\n"
            "    Media was referenced in the XML file but not previously uploaded to sipi:\n"
            "    The file 'no_upload.csv' was saved in '.' with the resource IDs and filenames."
        )
        res_msg = IngestInformation(
            [
                "unused_media0",
                "unused_media1",
                "unused_media2",
                "unused_media3",
                "unused_media4",
                "unused_media5",
                "unused_media6",
                "unused_media7",
                "unused_media8",
                "unused_media9",
                "unused_media10",
            ],
            [
                "no_up0",
                "no_up1",
                "no_up2",
                "no_up3",
                "no_up4",
                "no_up5",
                "no_up6",
                "no_up7",
                "no_up8",
                "no_up9",
                "no_up10",
            ],
        )._get_error_msg(Path(), "unused_media.csv", "no_upload.csv")
        assert res_msg == expected


def test_unused_media_to_df() -> None:
    unused_media_list = [
        "unused_media0",
        "unused_media1",
        "unused_media2",
        "unused_media3",
        "unused_media4",
        "unused_media5",
        "unused_media6",
        "unused_media7",
        "unused_media8",
        "unused_media9",
        "unused_media10",
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
                "ID_no_up4",
                "ID_no_up5",
                "ID_no_up6",
                "ID_no_up7",
                "ID_no_up8",
                "ID_no_up9",
                "ID_no_up10",
            ],
            "Filepath": [
                "fileno_up0.jpg",
                "fileno_up1.jpg",
                "fileno_up2.jpg",
                "fileno_up3.jpg",
                "fileno_up4.jpg",
                "fileno_up5.jpg",
                "fileno_up6.jpg",
                "fileno_up7.jpg",
                "fileno_up8.jpg",
                "fileno_up9.jpg",
                "fileno_up10.jpg",
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
            ("ID_no_up4", "fileno_up4.jpg"),
            ("ID_no_up5", "fileno_up5.jpg"),
            ("ID_no_up6", "fileno_up6.jpg"),
            ("ID_no_up7", "fileno_up7.jpg"),
            ("ID_no_up8", "fileno_up8.jpg"),
            ("ID_no_up9", "fileno_up9.jpg"),
            ("ID_no_up10", "fileno_up10.jpg"),
        ],
    )._no_uuid_to_df()
    assert_frame_equal(res_df, expected)


def test_no_uuid_to_df_not_enough() -> None:
    assert not IngestInformation([], [("ID_no_up0", "fileno_up0.jpg")])._unused_media_to_df()
