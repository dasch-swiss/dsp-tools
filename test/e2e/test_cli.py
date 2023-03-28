import subprocess
import unittest

from dsp_tools.models.exceptions import UserError

class TestCLI(unittest.TestCase):

    def test_subdomain_admin(self) -> None:
        wrong_servers = [
            "http://admin.dasch.swiss",
            "http://admin.test.dasch.swiss/",
            "https://admin.staging.dasch.swiss",
            "https://admin.dev-02.dasch.swiss/",
            "http://admin.082e-test-server.dasch.swiss"
        ]
        for server in wrong_servers:
            # TODO: doesn't work, because UserError is caught and printed. Watch stderr/stdout instead
            with self.assertRaisesRegex(
                UserError, 
                r"You try to address the subdomain 'admin' of a DSP server, "
                r"but DSP servers must be addressed on their 'api' subdomain, e\.g\. https://api\.dasch\.swiss\."
            ):
                subprocess.run(f"dsp-tools create -s {server} -u hans@muster.ch -p 1234 data_model.json", shell=True)
