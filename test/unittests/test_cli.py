"""unit tests for the command line interface"""

import unittest

import pytest

from dsp_tools.dsp_tools import _derive_sipi_url, _make_parser, _parse_arguments

from dsp_tools.models.exceptions import UserError


class TestCLI(unittest.TestCase):
    """
    unit tests for the command line interface
    """

    default_dsp_api_url = "http://0.0.0.0:3333"
    default_sipi_url = "http://0.0.0.0:1024"
    root_user_email = "root@example.com"
    root_user_pw = "test"
    parser = _make_parser(
        default_dsp_api_url=default_dsp_api_url,
        root_user_email=root_user_email,
        root_user_pw=root_user_pw,
    )
    positive_testcases = {
        "https://0.0.0.0:3333/": [
            default_dsp_api_url,
            default_sipi_url,
        ],
        "0.0.0.0:3333": [
            default_dsp_api_url,
            default_sipi_url,
        ],
        "localhost:3333": [
            default_dsp_api_url,
            default_sipi_url,
        ],
        "https://admin.dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "https://api.dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "https://app.dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "https://iiif.dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "https://dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "dasch.swiss": [
            "https://api.dasch.swiss",
            "https://iiif.dasch.swiss",
        ],
        "http://admin.test.dasch.swiss/": [
            "https://api.test.dasch.swiss",
            "https://iiif.test.dasch.swiss",
        ],
        "http://app.staging.dasch.swiss/": [
            "https://api.staging.dasch.swiss",
            "https://iiif.staging.dasch.swiss",
        ],
        "http://api.dev.dasch.swiss/": [
            "https://api.dev.dasch.swiss",
            "https://iiif.dev.dasch.swiss",
        ],
        "082a-test-server.dasch.swiss": [
            "https://api.082a-test-server.dasch.swiss",
            "https://iiif.082a-test-server.dasch.swiss",
        ],
        "admin.08F4-test-server.dasch.swiss": [
            "https://api.08f4-test-server.dasch.swiss",
            "https://iiif.08f4-test-server.dasch.swiss",
        ],
        "app.08F4-test-server.dasch.swiss": [
            "https://api.08f4-test-server.dasch.swiss",
            "https://iiif.08f4-test-server.dasch.swiss",
        ],
        "iiif.E5bC-test-server.dasch.swiss": [
            "https://api.e5bc-test-server.dasch.swiss",
            "https://iiif.e5bc-test-server.dasch.swiss",
        ],
    }

    def test_derive_sipi_url_positive_cases(self) -> None:
        """
        Test the method that derives the SIPI URL from the DSP API URL (positive test cases only)
        """
        for api_url_orig, expected in self.positive_testcases.items():
            api_url_canonical, sipi_url = expected
            user_args = ["xmlupload", "-s", api_url_orig, "-u", "some.user@dasch.swiss", "-p", "password", "data.xml"]
            args = _parse_arguments(
                user_args=user_args,
                parser=self.parser,
            )
            args = _derive_sipi_url(
                parsed_arguments=args,
                default_dsp_api_url=self.default_dsp_api_url,
                default_sipi_url=self.default_sipi_url,
            )
            self.assertEqual(args.server, api_url_canonical)
            self.assertEqual(args.sipi_url, sipi_url)

    def test_derive_sipi_url_negative_cases(self) -> None:
        """
        Test the method that derives the SIPI URL from the DSP API URL (negative test cases only)
        """
        invalid_inputs = [
            "https://0.0.0.0:1234",
            "https://invalid.dasch.swiss",
            "https://api.unkown-host.ch",
        ]
        for inv in invalid_inputs:
            user_args = ["xmlupload", "-s", inv, "-u", "some.user@dasch.swiss", "-p", "password", "data.xml"]
            args = _parse_arguments(
                user_args=user_args,
                parser=self.parser,
            )
            with self.assertRaisesRegex(UserError, r"Invalid DSP server URL"):
                args = _derive_sipi_url(
                    parsed_arguments=args,
                    default_dsp_api_url=self.default_dsp_api_url,
                    default_sipi_url=self.default_sipi_url,
                )


if __name__ == "__main__":
    pytest.main([__file__])
