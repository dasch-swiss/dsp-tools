import subprocess
import unittest


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
            completed_process = subprocess.run(f"dsp-tools create -s {server} -u hans@muster.ch -p 1234 data_model.json", shell=True, capture_output=True)
            stdout = completed_process.stdout.decode("utf-8")
            self.assertRegex(
                text=stdout,
                expected_regex=
                    r"You try to address the subdomain 'admin' of a DSP server, "
                    r"but DSP servers must be addressed on their 'api' subdomain, e\.g\. https://api\.dasch\.swiss\."
            )
                
