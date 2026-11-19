import pytest

from dsp_tools.commands.xmlupload.models.input_problems import AllIIIFUriProblems
from dsp_tools.commands.xmlupload.models.input_problems import IIIFHostRefused
from dsp_tools.commands.xmlupload.models.input_problems import IIIFProblemCategory
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
        "    - Please contact the dsp-tools development team (at support@dasch.swiss) with this information."
    )


@pytest.mark.parametrize(
    ("status_code", "exception_name", "expected"),
    [
        (200, None, IIIFProblemCategory.INVALID),
        (400, None, IIIFProblemCategory.INVALID),
        (404, None, IIIFProblemCategory.INVALID),
        (401, None, IIIFProblemCategory.ACCESS_REFUSED),
        (403, None, IIIFProblemCategory.ACCESS_REFUSED),
        (429, None, IIIFProblemCategory.ACCESS_REFUSED),
        (500, None, IIIFProblemCategory.UNREACHABLE),
        (503, None, IIIFProblemCategory.UNREACHABLE),
        (None, "ConnectTimeout", IIIFProblemCategory.UNREACHABLE),
    ],
)
def test_iiif_uri_problem_category(
    status_code: int | None, exception_name: str | None, expected: IIIFProblemCategory
) -> None:
    problem = IIIFUriProblem(
        uri="http://www.example.org/",
        regex_has_passed=False,
        status_code=status_code,
        raised_exception_name=exception_name,
    )
    assert problem.category == expected


@pytest.fixture
def refused_host() -> IIIFHostRefused:
    return IIIFHostRefused(
        host="iiif.ub.unibe.ch",
        status_code=403,
        unverified_uris=["https://iiif.ub.unibe.ch/a/full/max/0/default.jpg"],
    )


def test_iiif_host_refused_msg(refused_host: IIIFHostRefused) -> None:
    refused_host.unverified_uris.append("https://iiif.ub.unibe.ch/b/full/max/0/default.jpg")
    assert refused_host.get_msg() == (
        "IIIF server: iiif.ub.unibe.ch\n"
        "    - The server refused access to dsp-tools. Status code: 403\n"
        "    - Number of IIIF URI(s) that were not checked: 2\n"
        "    - Some IIIF servers accept automated requests only from their own network or VPN."
    )


def test_all_warning_msg_has_only_invalid(
    iiif_exception: IIIFUriProblem, iiif_uri_problem_ok_regex: IIIFUriProblem, refused_host: IIIFHostRefused
) -> None:
    problem = AllIIIFUriProblems(problems=[iiif_exception, iiif_uri_problem_ok_regex], refused_hosts=[refused_host])
    assert problem.get_warning_msg() == (
        "There were problems with the following IIIF URI(s):\n"
        "----------------------------\n"
        "URI: https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2\n"
        "    - Passed the internal regex check.\n"
        "    - The server did not respond as expected.\n"
        "    - Status code: 404"
    )


def test_all_info_msg_has_refused_hosts_and_unreachable(
    iiif_exception: IIIFUriProblem, iiif_uri_problem_ok_regex: IIIFUriProblem, refused_host: IIIFHostRefused
) -> None:
    problem = AllIIIFUriProblems(problems=[iiif_exception, iiif_uri_problem_ok_regex], refused_hosts=[refused_host])
    assert problem.get_info_msg() == (
        "The following IIIF URI(s) could not be checked:\n"
        "----------------------------\n"
        "IIIF server: iiif.ub.unibe.ch\n"
        "    - The server refused access to dsp-tools. Status code: 403\n"
        "    - Number of IIIF URI(s) that were not checked: 1\n"
        "    - Some IIIF servers accept automated requests only from their own network or VPN."
        "\n----------------------------\n"
        "URI: http://www.example.org/\n"
        "    - Did not pass the internal regex check.\n"
        "    - An error occurred during the network call: RequestException"
    )


def test_all_no_msg_if_category_empty(iiif_uri_problem_ok_regex: IIIFUriProblem) -> None:
    problem = AllIIIFUriProblems(problems=[iiif_uri_problem_ok_regex], refused_hosts=[])
    assert problem.get_info_msg() is None


if __name__ == "__main__":
    pytest.main([__file__])
