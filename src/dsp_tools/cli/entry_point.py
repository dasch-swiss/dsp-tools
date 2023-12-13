"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import subprocess
import sys
from importlib.metadata import version

import regex

from dsp_tools.cli.call_action import call_requested_action
from dsp_tools.cli.create_parsers import make_parser
from dsp_tools.models.exceptions import BaseError, InternalError, UserError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """
    Main entry point of the program as referenced in pyproject.toml
    """
    run(sys.argv[1:])


def run(args: list[str]) -> None:
    """
    Main function of the CLI.

    Args:
        args: a list of arguments passed by the user from the command line,
            excluding the leading "dsp-tools" command.

    Raises:
        UserError: if user input was wrong
        InputError: if user input was wrong
        InternalError: if the user cannot fix it
        RetryError: if the problem may disappear when trying again later
    """
    default_dsp_api_url = "http://0.0.0.0:3333"
    default_sipi_url = "http://0.0.0.0:1024"
    root_user_email = "root@example.com"
    root_user_pw = "test"

    parser = make_parser(
        default_dsp_api_url=default_dsp_api_url,
        root_user_email=root_user_email,
        root_user_pw=root_user_pw,
    )
    parsed_arguments = _parse_arguments(
        user_args=args,
        parser=parser,
    )
    _log_cli_arguments(parsed_arguments)

    try:
        parsed_arguments = _derive_sipi_url(
            parsed_arguments=parsed_arguments,
            default_dsp_api_url=default_dsp_api_url,
            default_sipi_url=default_sipi_url,
        )
        success = call_requested_action(parsed_arguments)
    except BaseError as err:
        logger.error(err)
        print("\nThe process was terminated because of an Error:")
        print(err.message)
        sys.exit(1)
    except Exception as err:  # noqa: BLE001 (blind-except)
        logger.error(err)
        raise InternalError from None

    if not success:
        logger.error("Terminate without success")
        sys.exit(1)


def _parse_arguments(
    user_args: list[str],
    parser: argparse.ArgumentParser,
) -> argparse.Namespace:
    """
    Parse the user-provided CLI arguments.
    If no action is provided,
    print the help text and exit with error code 1.

    Args:
        user_args: user-provided CLI arguments
        parser: parser used to parse the arguments

    Returns:
        parsed arguments
    """
    args = parser.parse_args(user_args)
    if not hasattr(args, "action"):
        parser.print_help(sys.stderr)
        sys.exit(1)
    return args


def _get_version() -> str:
    result = subprocess.run("pip freeze | grep dsp-tools", check=False, shell=True, capture_output=True)
    _detail_version = result.stdout.decode("utf-8")
    # _detail_version has one of the following formats:
    # - 'dsp-tools==5.0.3\n'
    # - 'dsp-tools @ git+https://github.com/dasch-swiss/dsp-tools.git@1f95f8d1b79bd5170a652c0d04e7ada417d76734\n'
    # - '-e git+ssh://git@github.com/dasch-swiss/dsp-tools.git@af9a35692b542676f2aa0a802ca7fc3b35f5713d#egg=dsp_tools\n'
    # - ''
    if version_number := regex.search(r"\d+\.\d+\.\d+", _detail_version):
        return version_number.group(0)
    if regex.search(r"github.com", _detail_version):
        return _detail_version.replace("\n", "")
    return version("dsp-tools")


def _log_cli_arguments(parsed_args: argparse.Namespace) -> None:
    """
    Log the CLI arguments passed by the user from the command line.

    Args:
        parsed_args: parsed arguments
    """
    metadata_lines = [
        f"DSP-TOOLS: Called the action '{parsed_args.action}' from the command line",
        f"DSP-TOOLS version: {_get_version()}",
        f"Location of this installation: {__file__}",
        "CLI arguments:",
    ]
    metadata_lines = [f"*** {line}" for line in metadata_lines]

    parameter_lines = []
    parameters_to_log = {key: value for key, value in vars(parsed_args).items() if key != "action"}
    longest_key_length = max((len(key) for key in parameters_to_log), default=0)
    for key, value in parameters_to_log.items():
        if key == "password":
            parameter_lines.append(f"{key:<{longest_key_length}} = {'*' * len(value)}")
        else:
            parameter_lines.append(f"{key:<{longest_key_length}} = {value}")
    parameter_lines = parameter_lines or ["(no parameters)"]
    parameter_lines = [f"***   {line}" for line in parameter_lines]

    asterisk_count = max(len(line) for line in metadata_lines + parameter_lines)
    logger.info("*" * asterisk_count)
    for line in metadata_lines:
        logger.info(line)
    for line in parameter_lines:
        logger.info(line)
    logger.info("*" * asterisk_count)


def _get_canonical_server_and_sipi_url(
    server: str,
    default_dsp_api_url: str,
    default_sipi_url: str,
) -> tuple[str, str]:
    """
    Based on the DSP server URL passed by the user,
    transform it to its canonical form,
    and derive the SIPI URL from it.

    If the DSP server URL points to port 3333 on localhost,
    the SIPI URL will point to port 1024 on localhost.

    If the DSP server URL points to a remote server ending in "dasch.swiss",
    modify it (if necessary) to point to the "api" subdomain of that server,
    and add a new "sipi_url" argument pointing to the "iiif" subdomain of that server.

    Args:
        server: DSP server URL passed by the user
        default_dsp_api_url: default DSP server on localhost
        default_sipi_url: default SIPI server on localhost

    Raises:
        UserError: if the DSP server URL passed by the user is invalid

    Returns:
        canonical DSP URL and SIPI URL
    """
    localhost_match = regex.search(r"(0\.0\.0\.0|localhost):3333", server)
    remote_url_match = regex.search(r"^(?:https?:\/\/)?(?:admin\.|api\.|iiif\.|app\.)?((?:.+\.)?dasch)\.swiss", server)

    if localhost_match:
        server = default_dsp_api_url
        sipi_url = default_sipi_url
    elif remote_url_match:
        server = f"https://api.{remote_url_match.group(1)}.swiss"
        sipi_url = f"https://iiif.{remote_url_match.group(1)}.swiss"
    else:
        logger.error(f"Invalid DSP server URL '{server}'")
        raise UserError(f"ERROR: Invalid DSP server URL '{server}'")

    logger.info(f"Using DSP server '{server}' and SIPI server '{sipi_url}'")
    print(f"Using DSP server '{server}' and SIPI server '{sipi_url}'")

    return server, sipi_url


def _derive_sipi_url(
    parsed_arguments: argparse.Namespace,
    default_dsp_api_url: str,
    default_sipi_url: str,
) -> argparse.Namespace:
    """
    Modify the parsed arguments so that the DSP and SIPI URLs are correct.
    Based on the DSP server URL passed by the user,
    transform it to its canonical form,
    and derive the SIPI URL from it.

    Args:
        parsed_arguments: CLI arguments passed by the user, parsed by argparse
        default_dsp_api_url: default DSP server on localhost
        default_sipi_url: default SIPI server on localhost

    Raises:
        UserError: if the DSP server URL passed by the user is invalid

    Returns:
        the modified arguments
    """
    if not hasattr(parsed_arguments, "server"):
        # some CLI actions (like excel2json, excel2xml, start-stack, ...) don't have a server at all
        return parsed_arguments

    server, sipi_url = _get_canonical_server_and_sipi_url(
        server=parsed_arguments.server,
        default_dsp_api_url=default_dsp_api_url,
        default_sipi_url=default_sipi_url,
    )
    parsed_arguments.server = server
    parsed_arguments.sipi_url = sipi_url

    return parsed_arguments


if __name__ == "__main__":
    main()
