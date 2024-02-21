"""unit tests for the command line interface"""

import argparse
import unittest

from dsp_tools.cli.entry_point import _derive_sipi_url, _get_canonical_server_and_sipi_url
from dsp_tools.models.exceptions import UserError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestCLI(unittest.TestCase):
    """
    unit tests for the command line interface
    """

    default_dsp_api_url = "http://0.0.0.0:3333"
    default_sipi_url = "http://0.0.0.0:1024"
    root_user_email = "root@example.com"
    root_user_pw = "test"
    positive_testcases: dict[str, list[str]]
    negative_testcases: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        """
        Populate the positive testcases and the negative testcases.
        Is executed once before the methods of this class are run.
        """
        cls.positive_testcases = {
            "https://0.0.0.0:3333/": [
                cls.default_dsp_api_url,
                cls.default_sipi_url,
            ],
            "0.0.0.0:3333": [
                cls.default_dsp_api_url,
                cls.default_sipi_url,
            ],
            "localhost:3333": [
                cls.default_dsp_api_url,
                cls.default_sipi_url,
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
            "https://demo.dasch.swiss/": [
                "https://api.demo.dasch.swiss",
                "https://iiif.demo.dasch.swiss",
            ],
            "http://api.dev.dasch.swiss/": [
                "https://api.dev.dasch.swiss",
                "https://iiif.dev.dasch.swiss",
            ],
            "dev-02.dasch.swiss": [
                "https://api.dev-02.dasch.swiss",
                "https://iiif.dev-02.dasch.swiss",
            ],
            "082a-test-server.dasch.swiss": [
                "https://api.082a-test-server.dasch.swiss",
                "https://iiif.082a-test-server.dasch.swiss",
            ],
            "admin.08F4-test-server.dasch.swiss": [
                "https://api.08F4-test-server.dasch.swiss",
                "https://iiif.08F4-test-server.dasch.swiss",
            ],
            "app.08F4-test-server.dasch.swiss": [
                "https://api.08F4-test-server.dasch.swiss",
                "https://iiif.08F4-test-server.dasch.swiss",
            ],
            "iiif.E5bC-test-server.dasch.swiss": [
                "https://api.E5bC-test-server.dasch.swiss",
                "https://iiif.E5bC-test-server.dasch.swiss",
            ],
            "not-yet-0826-test-server.dasch.swiss": [
                "https://api.not-yet-0826-test-server.dasch.swiss",
                "https://iiif.not-yet-0826-test-server.dasch.swiss",
            ],
            "https://admin.ls-prod-server.dasch.swiss": [
                "https://api.ls-prod-server.dasch.swiss",
                "https://iiif.ls-prod-server.dasch.swiss",
            ],
            "https://ls-test-server.dasch.swiss": [
                "https://api.ls-test-server.dasch.swiss",
                "https://iiif.ls-test-server.dasch.swiss",
            ],
        }
        cls.negative_testcases = [
            "https://0.0.0.0:1234",
            "https://api.unkown-host.ch",
        ]

    def test_derive_sipi_url_without_server(self) -> None:
        """
        If the argparse.Namespace does not contain a server,
        the function should return the same object.
        """
        args_without_server = argparse.Namespace(
            action="xmlupload",
            xmlfile="data.xml",
        )
        args_returned = _derive_sipi_url(
            parsed_arguments=args_without_server,
            default_dsp_api_url=self.default_dsp_api_url,
            default_sipi_url=self.default_sipi_url,
        )
        self.assertEqual(args_without_server, args_returned)

    def test_derive_sipi_url_with_server(self) -> None:
        """
        If the argparse.Namespace contains a server,
        the function should return a modified argparse.Namespace,
        with the correct DSP URL and SIPI URL.
        """
        args_with_server = argparse.Namespace(
            action="xmlupload",
            server="dasch.swiss",
            user="some.user@dasch.swiss",
            password="password",
            xmlfile="data.xml",
        )
        args_returned = _derive_sipi_url(
            parsed_arguments=args_with_server,
            default_dsp_api_url=self.default_dsp_api_url,
            default_sipi_url=self.default_sipi_url,
        )
        args_expected = argparse.Namespace(
            action="xmlupload",
            server="https://api.dasch.swiss",
            sipi_url="https://iiif.dasch.swiss",
            user="some.user@dasch.swiss",
            password="password",
            xmlfile="data.xml",
        )
        self.assertEqual(args_expected, args_returned)

    def test_get_canonical_server_and_sipi_url(self) -> None:
        """
        Test the method that canonicalizes the DSP URL and derives the SIPI URL from it.
        """
        for api_url_orig, expected in self.positive_testcases.items():
            api_url_expected, sipi_url_expected = expected
            api_url_returned, sipi_url_returned = _get_canonical_server_and_sipi_url(
                server=api_url_orig,
                default_dsp_api_url=self.default_dsp_api_url,
                default_sipi_url=self.default_sipi_url,
            )
            self.assertEqual(api_url_expected, api_url_returned)
            self.assertEqual(sipi_url_expected, sipi_url_returned)

        for invalid in self.negative_testcases:
            with self.assertRaisesRegex(UserError, r"Invalid DSP server URL"):
                _ = _get_canonical_server_and_sipi_url(
                    server=invalid,
                    default_dsp_api_url=self.default_dsp_api_url,
                    default_sipi_url=self.default_sipi_url,
                )
