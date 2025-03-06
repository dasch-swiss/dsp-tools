import subprocess
import sys

from dsp_tools.utils.ansi_colors import BOLD_GREEN
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def main() -> None:
    """
    Wrapper for markdown-link-validator.
    markdown-link-validator is a tool that checks the links in Markdown files.
    It prints every single link to the console, and returns a non-zero exit code if there are any errors.
    This script converts the output to a user-friendly short error message.
    """
    cli_command = "just check-links"
    if _get_return_code(cli_command) != 0:
        msg = f"markdown-link-validator reported an error. Run this command to see more details: {cli_command}"
        print(f"{BOLD_RED}{msg}{RESET_TO_DEFAULT}")
        sys.exit(1)
    else:
        msg = "markdown-link-validator: No errors found"
        print(f"{BOLD_GREEN}{msg}{RESET_TO_DEFAULT}")


def _get_return_code(call: str) -> int:
    try:
        res = subprocess.run(call.split(), capture_output=True, check=True, encoding="utf-8")
        return res.returncode
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == "__main__":
    main()
