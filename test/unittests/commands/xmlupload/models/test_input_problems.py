import pytest

from dsp_tools.commands.xmlupload.models.input_problems import AllIIIFUriProblems
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


@pytest.fixture
def iiif_exception() -> IIIFUriProblem:
    return IIIFUriProblem(
        uri="http://www.example.org/",
        regex_has_passed=False,
        raised_exception_name="RequestException",
    )


@pytest.fixture
def iiif_uri_problem_ok_regex() -> IIIFUriProblem:
    return IIIFUriProblem(
        uri="https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
        regex_has_passed=True,
        status_code=404,
    )


@pytest.fixture
def iiif_uri_problem_bad_regex() -> IIIFUriProblem:
    return IIIFUriProblem(
        uri="http://www.example.org/",
        regex_has_passed=False,
        status_code=404,
    )


@pytest.fixture
def iiif_uri_problem_bad_regex_good_status_code() -> IIIFUriProblem:
    return IIIFUriProblem(
        uri="http://www.example.org/",
        regex_has_passed=False,
        status_code=200,
    )


def test_iiif_uri_problem_ok_regex(iiif_uri_problem_ok_regex: IIIFUriProblem) -> None:
    assert iiif_uri_problem_ok_regex.get_msg() == (
        "URI: https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2\n"
        "    - Passed the internal regex check.\n"
        "    - The server did not respond as expected.\n"
        "    - Status code: 404"
    )


def test_iiif_uri_problem_bad_regex(iiif_uri_problem_bad_regex: IIIFUriProblem) -> None:
    assert iiif_uri_problem_bad_regex.get_msg() == (
        "URI: http://www.example.org/\n"
        "    - Did not pass the internal regex check.\n"
        "    - The server did not respond as expected.\n"
        "    - Status code: 404"
    )


def test_iiif_uri_problem_exception(iiif_exception: IIIFUriProblem) -> None:
    assert iiif_exception.get_msg() == (
        "URI: http://www.example.org/\n"
        "    - Did not pass the internal regex check.\n"
        "    - An error occurred during the network call: RequestException"
    )


def test_failing_regex(iiif_uri_problem_bad_regex_good_status_code: IIIFUriProblem) -> None:
    assert iiif_uri_problem_bad_regex_good_status_code.get_msg() == (
        "URI: http://www.example.org/\n"
        "    - Did not pass the internal regex check.\n"
        "    - Although the IIIF-server responded as expected, this URI did not pass validation.\n"
        "    - Please contact the dsp-tools development team with this information."
    )


def test_all(iiif_exception: IIIFUriProblem, iiif_uri_problem_ok_regex: IIIFUriProblem) -> None:
    problem = AllIIIFUriProblems(problems=[iiif_exception, iiif_uri_problem_ok_regex])
    assert problem.get_msg() == (
        "There were problems with the following IIIF URI(s):\n"
        "----------------------------\n"
        "URI: http://www.example.org/\n"
        "    - Did not pass the internal regex check.\n"
        "    - An error occurred during the network call: RequestException"
        "\n----------------------------\n"
        "URI: https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2\n"
        "    - Passed the internal regex check.\n"
        "    - The server did not respond as expected.\n"
        "    - Status code: 404"
    )


if __name__ == "__main__":
    pytest.main([__file__])
