"""unit tests for the command line interface"""

import argparse

import pytest

from dsp_tools.cli.entry_point import _derive_dsp_ingest_url
from dsp_tools.cli.entry_point import _get_canonical_server_and_dsp_ingest_url
from dsp_tools.error.exceptions import InputError

DEFAULT_DSP_API_URL = "http://0.0.0.0:3333"
DEFAULT_DSP_INGEST_URL = "http://0.0.0.0:3340"


@pytest.fixture
def unsupported_urls() -> list[str]:
    return [
        "https://0.0.0.0:1234",
        "https://api.unkown-host.ch",
    ]


def test_derive_dsp_ingest_url_without_server() -> None:
    """
    If the argparse.Namespace does not contain a server,
    the function should return the same object.
    """
    args_without_server = argparse.Namespace(
        action="xmlupload",
        xmlfile="data.xml",
    )
    args_returned = _derive_dsp_ingest_url(
        parsed_arguments=args_without_server,
        default_dsp_api_url=DEFAULT_DSP_API_URL,
        default_dsp_ingest_url=DEFAULT_DSP_INGEST_URL,
    )
    assert args_without_server == args_returned


def test_derive_dsp_ingest_url_with_server() -> None:
    """
    If the argparse.Namespace contains a server,
    the function should return a modified argparse.Namespace,
    with the correct DSP URL and Ingest URL.
    """
    args_with_server = argparse.Namespace(
        action="xmlupload",
        server="dasch.swiss",
        user="some.user@dasch.swiss",
        password="password",
        xmlfile="data.xml",
    )
    args_returned = _derive_dsp_ingest_url(
        parsed_arguments=args_with_server,
        default_dsp_api_url=DEFAULT_DSP_API_URL,
        default_dsp_ingest_url=DEFAULT_DSP_INGEST_URL,
    )
    args_expected = argparse.Namespace(
        action="xmlupload",
        server="https://api.dasch.swiss",
        dsp_ingest_url="https://ingest.dasch.swiss",
        user="some.user@dasch.swiss",
        password="password",
        xmlfile="data.xml",
    )
    assert args_expected == args_returned


@pytest.mark.parametrize(
    ("api_url_orig", "api_url_expected", "dsp_ingest_url_expected"),
    [
        ("https://0.0.0.0:3333/", DEFAULT_DSP_API_URL, DEFAULT_DSP_INGEST_URL),
        ("0.0.0.0:3333", DEFAULT_DSP_API_URL, DEFAULT_DSP_INGEST_URL),
        ("localhost:3333", DEFAULT_DSP_API_URL, DEFAULT_DSP_INGEST_URL),
        ("https://admin.dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("https://api.dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("https://app.dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("https://ingest.dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("https://dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("dasch.swiss", "https://api.dasch.swiss", "https://ingest.dasch.swiss"),
        ("http://admin.test.dasch.swiss/", "https://api.test.dasch.swiss", "https://ingest.test.dasch.swiss"),
        ("http://app.staging.dasch.swiss/", "https://api.staging.dasch.swiss", "https://ingest.staging.dasch.swiss"),
        ("https://demo.dasch.swiss/", "https://api.demo.dasch.swiss", "https://ingest.demo.dasch.swiss"),
        ("http://api.dev.dasch.swiss/", "https://api.dev.dasch.swiss", "https://ingest.dev.dasch.swiss"),
        ("dev-02.dasch.swiss", "https://api.dev-02.dasch.swiss", "https://ingest.dev-02.dasch.swiss"),
        (
            "082a-test-server.dasch.swiss",
            "https://api.082a-test-server.dasch.swiss",
            "https://ingest.082a-test-server.dasch.swiss",
        ),
        (
            "admin.08F4-test-server.dasch.swiss",
            "https://api.08F4-test-server.dasch.swiss",
            "https://ingest.08F4-test-server.dasch.swiss",
        ),
        (
            "app.08F4-test-server.dasch.swiss",
            "https://api.08F4-test-server.dasch.swiss",
            "https://ingest.08F4-test-server.dasch.swiss",
        ),
        (
            "ingest.08F4-test-server.dasch.swiss",
            "https://api.08F4-test-server.dasch.swiss",
            "https://ingest.08F4-test-server.dasch.swiss",
        ),
        (
            "not-yet-0826-test-server.dasch.swiss",
            "https://api.not-yet-0826-test-server.dasch.swiss",
            "https://ingest.not-yet-0826-test-server.dasch.swiss",
        ),
        (
            "https://admin.ls-prod-server.dasch.swiss",
            "https://api.ls-prod-server.dasch.swiss",
            "https://ingest.ls-prod-server.dasch.swiss",
        ),
        (
            "https://ls-test-server.dasch.swiss",
            "https://api.ls-test-server.dasch.swiss",
            "https://ingest.ls-test-server.dasch.swiss",
        ),
    ],
)
def test_supported_urls(api_url_orig: str, api_url_expected: str, dsp_ingest_url_expected: str) -> None:
    """
    Test the method that canonicalizes the DSP URL and derives the SIPI URL from it.
    """
    api_url_returned, dsp_ingest_url_returned = _get_canonical_server_and_dsp_ingest_url(
        server=api_url_orig,
        default_dsp_api_url=DEFAULT_DSP_API_URL,
        default_dsp_ingest_url=DEFAULT_DSP_INGEST_URL,
    )
    assert api_url_expected == api_url_returned
    assert dsp_ingest_url_expected == dsp_ingest_url_returned


@pytest.mark.parametrize(
    "unsupported_url",
    ["https://0.0.0.0:1234", "https://api.unkown-host.ch"],
)
def test_unsupported_cases(unsupported_url: str) -> None:
    with pytest.raises(InputError, match=r"Invalid DSP server URL"):
        _ = _get_canonical_server_and_dsp_ingest_url(
            server=unsupported_url,
            default_dsp_api_url=DEFAULT_DSP_API_URL,
            default_dsp_ingest_url=DEFAULT_DSP_INGEST_URL,
        )


if __name__ == "__main__":
    pytest.main([__file__])
