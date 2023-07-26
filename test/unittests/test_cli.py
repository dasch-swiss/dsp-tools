"""unit tests for the command line interface"""

import argparse
import unittest

import pytest

from dsp_tools.dsp_tools import _derive_sipi_url
from dsp_tools.models.exceptions import UserError


class TestCLI(unittest.TestCase):
    """
    unit tests for the command line interface
    """

    default_dsp_api_url = "http://0.0.0.0:3333"
    default_sipi_url = "http://0.0.0.0:1024"
    root_user_email = "root@example.com"
    root_user_pw = "test"
    positive_testcases: dict[str, list[str]]

    @classmethod
    def setUpClass(cls) -> None:
        """
        Is executed once before the methods of this class are run
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

    def test_derive_sipi_url(self) -> None:
        """
        Test the method that derives the SIPI URL from the DSP API URL
        """
        for api_url_orig, expected in self.positive_testcases.items():
            api_url_canonical, sipi_url = expected
            args_orig = argparse.Namespace(
                action="xmlupload",
                server=api_url_orig,
                user="some.user@dasch.swiss",
                password="password",
                xmlfile="data.xml",
            )
            args_new = _derive_sipi_url(
                parsed_arguments=args_orig,
                default_dsp_api_url=self.default_dsp_api_url,
                default_sipi_url=self.default_sipi_url,
            )
            self.assertEqual(args_new.server, api_url_canonical)
            self.assertEqual(args_new.sipi_url, sipi_url)  # pylint: disable=no-member

        invalid_inputs = [
            "https://0.0.0.0:1234",
            "https://api.unkown-host.ch",
        ]
        for inv in invalid_inputs:
            args_orig = argparse.Namespace(
                action="xmlupload",
                server=inv,
                user="some.user@dasch.swiss",
                password="password",
                xmlfile="data.xml",
            )
            with self.assertRaisesRegex(UserError, r"Invalid DSP server URL"):
                _ = _derive_sipi_url(
                    parsed_arguments=args_orig,
                    default_dsp_api_url=self.default_dsp_api_url,
                    default_sipi_url=self.default_sipi_url,
                )


if __name__ == "__main__":
    pytest.main([__file__])
