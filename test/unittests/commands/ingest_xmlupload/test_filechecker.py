from pathlib import Path

import pandas as pd
import pytest

from dsp_tools.commands.ingest_xmlupload.upload_files.filechecker import check_files
from dsp_tools.commands.ingest_xmlupload.upload_files.input_error import FileProblems


def test_check_files_success() -> None:
    supported_and_existing = {
        Path("testdata/bitstreams/test.txt"),
        Path("testdata/bitstreams/test.pdf"),
        Path("testdata/bitstreams/test,with,multiple,commas.png"),
        Path("testdata/bitstreams/test with whitespaces.png"),
        Path("testdata/bitstreams/test with uppercase extension.JPG"),
        Path("testdata/bitstreams/test.with.multiple.dots.png"),
    }
    res = check_files(supported_and_existing)
    assert not res


def test_check_files_unsupported() -> None:
    unsupported_paths = {
        Path("testdata/invalid-testdata/bitstreams/test.gif"),
        Path("testdata/invalid-testdata/bitstreams/test.rtf"),
    }
    res = check_files(unsupported_paths)
    expected = FileProblems([], list(unsupported_paths))
    assert res == expected


def test_check_files_non_existing() -> None:
    inexisting_paths = {Path("foo/bar.txt"), Path("egg/spam.pdf")}
    res = check_files(inexisting_paths)
    expected = FileProblems(list(inexisting_paths), [])
    assert res == expected


def test_check_files_non_existing_and_unsupported() -> None:
    inexisting_unsupported_paths = {Path("foo/bar.baz"), Path("egg/spam.ham")}
    res = check_files(inexisting_unsupported_paths)
    expected = FileProblems([], list(inexisting_unsupported_paths))
    assert res == expected


def test_check_files_mixed_unsupported() -> None:
    mixed_unsupported_paths = {Path("foo/bar.baz"), Path("testdata/invalid-testdata/bitstreams/test.gif")}
    res = check_files(mixed_unsupported_paths)
    expected = FileProblems([], list(mixed_unsupported_paths))
    assert res == expected


class TestFileProblems:
    def test_value_error(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011 (too broad exception clause)
            FileProblems([], [])

    def test_execute_error_protocol_nonexisting(self) -> None:
        file_problems = FileProblems([Path("foo/bar.txt"), Path("spam/eggs.pdf")], [])
        expected = (
            "Some files referenced in the <bitstream> tags of your XML file cannot be uploaded to the server.\n"
            "\n"
            "The following files don't exist on your computer:\n"
            " - foo/bar.txt\n"
            " - spam/eggs.pdf"
        )
        res = file_problems.execute_error_protocol()
        assert res == expected

    def test_execute_error_protocol_unsupported(self) -> None:
        file_problems = FileProblems([], [Path("testdata/bitstreams/test.txt"), Path("testdata/bitstreams/test.pdf")])
        expected = (
            "Some files referenced in the <bitstream> tags of your XML file cannot be uploaded to the server.\n"
            "\n"
            "The following files have unsupported extensions:\n"
            " - testdata/bitstreams/test.txt\n"
            " - testdata/bitstreams/test.pdf"
        )
        res = file_problems.execute_error_protocol()
        assert res == expected

    def test_execute_error_protocol_inexisting_and_unsupported(self) -> None:
        file_problems = FileProblems(
            [Path("foo/bar.txt"), Path("spam/eggs.pdf")],
            [Path("testdata/bitstreams/test.txt"), Path("testdata/bitstreams/test.pdf")],
        )
        expected = (
            "Some files referenced in the <bitstream> tags of your XML file cannot be uploaded to the server.\n"
            "\n"
            "The following files don't exist on your computer:\n"
            " - foo/bar.txt\n"
            " - spam/eggs.pdf\n"
            "\n"
            "The following files have unsupported extensions:\n"
            " - testdata/bitstreams/test.txt\n"
            " - testdata/bitstreams/test.pdf"
        )
        res = file_problems.execute_error_protocol()
        assert res == expected

    def test_execute_error_protocol_with_file_saving(self) -> None:
        file_problems = FileProblems(
            [Path("foo/bar.txt"), Path("spam/eggs.pdf")], [Path("testdata/bitstreams/test.pdf")], maximum_prints=2
        )
        expected = (
            "Some files referenced in the <bitstream> tags of your XML file cannot be uploaded to the server. "
            "The full list of files with problems has been saved to 'file_problems.csv'."
        )
        res = file_problems.execute_error_protocol()
        assert res == expected

        output_file = Path("file_problems.csv")
        df = pd.read_csv(output_file)

        data_expected = {
            "File": ["foo/bar.txt", "spam/eggs.pdf", "testdata/bitstreams/test.pdf"],
            "Problem": ["File doesn't exist", "File doesn't exist", "Extension not supported"],
        }
        df_expected = pd.DataFrame(data_expected)
        assert df.equals(df_expected)
        output_file.unlink()
