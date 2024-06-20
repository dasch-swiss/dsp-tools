from pathlib import Path

from dsp_tools.commands.ingest_xmlupload.upload_files.filechecker import FileProblems
from dsp_tools.commands.ingest_xmlupload.upload_files.filechecker import check_files


def test_check_files_success() -> None:
    res = check_files({Path("testdata/bitstreams/test.txt"), Path("testdata/bitstreams/test.pdf")})
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
