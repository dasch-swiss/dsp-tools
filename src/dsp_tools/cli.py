"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import datetime
import subprocess
import sys
from importlib.metadata import version

import regex

from dsp_tools.commands.excel2json.lists import excel2lists, validate_lists_section_with_schema
from dsp_tools.commands.excel2json.project import excel2json
from dsp_tools.commands.excel2json.properties import excel2properties
from dsp_tools.commands.excel2json.resources import excel2resources
from dsp_tools.commands.excel2xml.excel2xml_cli import excel2xml
from dsp_tools.commands.fast_xmlupload.process_files import process_files
from dsp_tools.commands.fast_xmlupload.upload_files import upload_files
from dsp_tools.commands.fast_xmlupload.upload_xml import fast_xmlupload
from dsp_tools.commands.id2iri import id2iri
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.project.create.project_create_lists import create_lists
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.project.get import get_project
from dsp_tools.commands.rosetta import upload_rosetta
from dsp_tools.commands.start_stack import StackConfiguration, StackHandler
from dsp_tools.commands.template import generate_template_repo
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig, UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import validate_xml_against_schema

logger = get_logger(__name__)


def _make_parser(
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> argparse.ArgumentParser:
    """
    Create a parser for the command line arguments.

    Args:
        default_dsp_api_url: URL of the DSP server (default value for localhost)
        root_user_email: username (e-mail) used for authentication with the DSP-API (default value for localhost)
        root_user_pw: password used for authentication with the DSP-API (default value for localhost)

    Returns:
        parser
    """
    # help texts
    username_text = "username (e-mail) used for authentication with the DSP-API"
    password_text = "password used for authentication with the DSP-API"
    dsp_server_text = "URL of the DSP server"
    verbose_text = "print more information about the progress to the console"

    # make a parser
    parser = argparse.ArgumentParser(
        description=f"DSP-TOOLS (version {version('dsp-tools')}, © {datetime.datetime.now().year} by DaSCH)"
    )
    subparsers = parser.add_subparsers(
        title="Subcommands", description="Valid subcommands are", help="sub-command help"
    )

    # create
    parser_create = subparsers.add_parser(
        name="create",
        help="Create a project defined in a JSON project file on a DSP server. "
        "A project can consist of lists, groups, users, and ontologies (data models).",
    )
    parser_create.set_defaults(action="create")
    parser_create.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    parser_create.add_argument("-u", "--user", default=root_user_email, help=username_text)
    parser_create.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    parser_create.add_argument(
        "-V",
        "--validate-only",
        action="store_true",
        help="validate the JSON file without creating it on the DSP server",
    )
    parser_create.add_argument(
        "-l",
        "--lists-only",
        action="store_true",
        help="create only the lists (prerequisite: the project exists on the server)",
    )
    parser_create.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_create.add_argument("-d", "--dump", action="store_true", help="write every request to DSP-API into a file")
    parser_create.add_argument("project_definition", help="path to the JSON project file")

    # get
    parser_get = subparsers.add_parser(
        name="get",
        help="Retrieve a project with its data model(s) from a DSP server and write it into a JSON file",
    )
    parser_get.set_defaults(action="get")
    parser_get.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    parser_get.add_argument("-u", "--user", default=root_user_email, help=username_text)
    parser_get.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    parser_get.add_argument("-P", "--project", help="shortcode, shortname or IRI of the project", required=True)
    parser_get.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_get.add_argument("-d", "--dump", action="store_true", help="write every request to DSP-API into a file")
    parser_get.add_argument("project_definition", help="path to the file the project should be written to")

    # xmlupload
    parser_upload = subparsers.add_parser(name="xmlupload", help="Upload data defined in an XML file to a DSP server")
    parser_upload.set_defaults(action="xmlupload")
    parser_upload.add_argument(
        "-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to"
    )
    parser_upload.add_argument("-u", "--user", default=root_user_email, help=username_text)
    parser_upload.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    parser_upload.add_argument(
        "-i", "--imgdir", default=".", help="folder from where the paths in the <bitstream> tags are evaluated"
    )
    parser_upload.add_argument(
        "-V", "--validate-only", action="store_true", help="validate the XML file without uploading it"
    )
    parser_upload.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_upload.add_argument(
        "-d", "--dump", action="store_true", help="write every request to DSP-API/SIPI into a file"
    )
    parser_upload.add_argument("xmlfile", help="path to the XML file containing the data")

    # process-files
    parser_process_files = subparsers.add_parser(
        name="process-files",
        help="For internal use only: process all files referenced in an XML file",
    )
    parser_process_files.set_defaults(action="process-files")
    parser_process_files.add_argument(
        "--input-dir", help="path to the input directory where the files should be read from"
    )
    parser_process_files.add_argument(
        "--output-dir", help="path to the output directory where the processed/transformed files should be written to"
    )
    parser_process_files.add_argument("--nthreads", type=int, default=None, help="number of threads to use")
    parser_process_files.add_argument("xml_file", help="path to XML file containing the data")

    # upload-files
    parser_upload_files = subparsers.add_parser(
        name="upload-files",
        help="For internal use only: upload already processed files",
    )
    parser_upload_files.set_defaults(action="upload-files")
    parser_upload_files.add_argument("-d", "--processed-dir", help="path to the directory with the processed files")
    parser_upload_files.add_argument("-n", "--nthreads", type=int, default=4, help="number of threads to use")
    parser_upload_files.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    parser_upload_files.add_argument("-u", "--user", default=root_user_email, help=username_text)
    parser_upload_files.add_argument("-p", "--password", default=root_user_pw, help=password_text)

    # fast-xmlupload
    parser_fast_xmlupload = subparsers.add_parser(
        name="fast-xmlupload",
        help="For internal use only: create resources with already uploaded files",
    )
    parser_fast_xmlupload.set_defaults(action="fast-xmlupload")
    parser_fast_xmlupload.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    parser_fast_xmlupload.add_argument("-u", "--user", default=root_user_email, help=username_text)
    parser_fast_xmlupload.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    parser_fast_xmlupload.add_argument("xml_file", help="path to XML file containing the data")

    # excel2json
    parser_excel2json = subparsers.add_parser(
        name="excel2json",
        help="Create an entire JSON project file from a folder containing the required Excel files",
    )
    parser_excel2json.set_defaults(action="excel2json")
    parser_excel2json.add_argument("excelfolder", help="path to the folder containing the Excel files")
    parser_excel2json.add_argument("project_definition", help="path to the output JSON file")

    # excel2lists
    parser_excel_lists = subparsers.add_parser(
        name="excel2lists",
        help="Create the 'lists' section of a JSON project file from one or multiple Excel files",
    )
    parser_excel_lists.set_defaults(action="excel2lists")
    parser_excel_lists.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_excel_lists.add_argument("excelfolder", help="path to the folder containing the Excel file(s)")
    parser_excel_lists.add_argument("lists_section", help="path to the output JSON file containing the 'lists' section")

    # excel2resources
    parser_excel_resources = subparsers.add_parser(
        name="excel2resources",
        help="Create the 'resources' section of a JSON project file from one or multiple Excel files",
    )
    parser_excel_resources.set_defaults(action="excel2resources")
    parser_excel_resources.add_argument("excelfile", help="path to the Excel file containing the resources")
    parser_excel_resources.add_argument(
        "resources_section", help="path to the output JSON file containing the 'resources' section"
    )

    # excel2properties
    parser_excel_properties = subparsers.add_parser(
        name="excel2properties",
        help="Create the 'properties' section of a JSON project file from one or multiple Excel files",
    )
    parser_excel_properties.set_defaults(action="excel2properties")
    parser_excel_properties.add_argument("excelfile", help="path to the Excel file containing the properties")
    parser_excel_properties.add_argument(
        "properties_section", help="path to the output JSON file containing the 'properties' section"
    )

    # excel2xml
    parser_excel2xml = subparsers.add_parser(
        name="excel2xml",
        help="Create an XML file from an Excel/CSV file that is already structured according to the DSP specifications",
    )
    parser_excel2xml.set_defaults(action="excel2xml")
    parser_excel2xml.add_argument("data_source", help="path to the CSV or XLS(X) file containing the data")
    parser_excel2xml.add_argument("project_shortcode", help="shortcode of the project that this data belongs to")
    parser_excel2xml.add_argument("ontology_name", help="name of the ontology that this data belongs to")

    # id2iri
    parser_id2iri = subparsers.add_parser(
        name="id2iri",
        help="Replace internal IDs of an XML file (resptr tags or salsah-links) by IRIs provided in a mapping file.",
    )
    parser_id2iri.set_defaults(action="id2iri")
    parser_id2iri.add_argument(
        "-r", "--remove-resources", action="store_true", help="remove resources if their ID is in the mapping"
    )
    parser_id2iri.add_argument("xmlfile", help="path to the XML file containing the data to be replaced")
    parser_id2iri.add_argument("mapping", help="path to the JSON file containing the mapping of IDs to IRIs")

    # startup DSP stack
    parser_stackup = subparsers.add_parser(name="start-stack", help="Run a local instance of DSP-API and DSP-APP")
    parser_stackup.set_defaults(action="start-stack")
    parser_stackup.add_argument(
        "--max_file_size",
        type=int,
        help="max. multimedia file size allowed by SIPI, in MB (default: 250, max: 100'000)",
    )
    parser_stackup.add_argument("--prune", action="store_true", help="execute 'docker system prune' without asking")
    parser_stackup.add_argument(
        "--no-prune", action="store_true", help="don't execute 'docker system prune' (and don't ask)"
    )
    parser_stackup.add_argument(
        "--latest",
        action="store_true",
        help="use the latest dev version of DSP-API, from the main branch of the GitHub repository",
    )

    # shutdown DSP-API
    parser_stackdown = subparsers.add_parser(
        name="stop-stack", help="Shut down the local instance of DSP-API and DSP-APP, and delete all data in it"
    )
    parser_stackdown.set_defaults(action="stop-stack")

    # create template repo with minimal JSON and XML files
    parser_template = subparsers.add_parser(
        name="template", help="Create a template repository with a minimal JSON and XML file"
    )
    parser_template.set_defaults(action="template")

    # clone rosetta
    parser_rosetta = subparsers.add_parser(
        name="rosetta", help="Clone the most up to data rosetta repository, create the data model and upload the data"
    )
    parser_rosetta.set_defaults(action="rosetta")

    return parser


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


def _call_requested_action(args: argparse.Namespace) -> bool:
    """
    Call the appropriate method of DSP-TOOLS.

    Args:
        args: parsed CLI arguments

    Raises:
        BaseError from the called methods
        UserError from the called methods
        unexpected errors from the called methods and underlying libraries

    Returns:
        success status
    """
    if args.action == "create":
        if args.lists_only:
            if args.validate_only:
                success = validate_lists_section_with_schema(args.project_definition)
                print("'Lists' section of the JSON project file is syntactically correct and passed validation.")
            else:
                _, success = create_lists(
                    project_file_as_path_or_parsed=args.project_definition,
                    server=args.server,
                    user=args.user,
                    password=args.password,
                    dump=args.dump,
                )
        else:
            if args.validate_only:
                success = validate_project(args.project_definition)
                print("JSON project file is syntactically correct and passed validation.")
            else:
                success = create_project(
                    project_file_as_path_or_parsed=args.project_definition,
                    server=args.server,
                    user_mail=args.user,
                    password=args.password,
                    verbose=args.verbose,
                    dump=args.dump,
                )
    elif args.action == "get":
        success = get_project(
            project_identifier=args.project,
            outfile_path=args.project_definition,
            server=args.server,
            user=args.user,
            password=args.password,
            verbose=args.verbose,
            dump=args.dump,
        )
    elif args.action == "xmlupload":
        if args.validate_only:
            success = validate_xml_against_schema(args.xmlfile)
        else:
            success = xmlupload(
                input_file=args.xmlfile,
                server=args.server,
                user=args.user,
                password=args.password,
                imgdir=args.imgdir,
                sipi=args.sipi_url,
                config=UploadConfig(diagnostics=DiagnosticsConfig(verbose=args.verbose, dump=args.dump)),
            )
    elif args.action == "process-files":
        success = process_files(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            xml_file=args.xml_file,
            nthreads=args.nthreads,
        )
    elif args.action == "upload-files":
        success = upload_files(
            dir_with_processed_files=args.processed_dir,
            nthreads=args.nthreads,
            user=args.user,
            password=args.password,
            dsp_url=args.server,
            sipi_url=args.sipi_url,
        )
    elif args.action == "fast-xmlupload":
        success = fast_xmlupload(
            xml_file=args.xml_file,
            user=args.user,
            password=args.password,
            dsp_url=args.server,
            sipi_url=args.sipi_url,
        )
    elif args.action == "excel2json":
        success = excel2json(
            data_model_files=args.excelfolder,
            path_to_output_file=args.project_definition,
        )
    elif args.action == "excel2lists":
        _, success = excel2lists(
            excelfolder=args.excelfolder,
            path_to_output_file=args.lists_section,
            verbose=args.verbose,
        )
    elif args.action == "excel2resources":
        _, success = excel2resources(
            excelfile=args.excelfile,
            path_to_output_file=args.resources_section,
        )
    elif args.action == "excel2properties":
        _, success = excel2properties(
            excelfile=args.excelfile,
            path_to_output_file=args.properties_section,
        )
    elif args.action == "id2iri":
        success = id2iri(
            xml_file=args.xmlfile,
            json_file=args.mapping,
            remove_resource_if_id_in_mapping=args.remove_resources,
        )
    elif args.action == "excel2xml":
        success, _ = excel2xml(
            datafile=args.data_source,
            shortcode=args.project_shortcode,
            default_ontology=args.ontology_name,
        )
    elif args.action == "start-stack":
        stack_handler = StackHandler(
            StackConfiguration(
                max_file_size=args.max_file_size,
                enforce_docker_system_prune=args.prune,
                suppress_docker_system_prune=args.no_prune,
                latest_dev_version=args.latest,
            )
        )
        success = stack_handler.start_stack()
    elif args.action == "stop-stack":
        stack_handler = StackHandler(StackConfiguration())
        success = stack_handler.stop_stack()
    elif args.action == "template":
        success = generate_template_repo()
    elif args.action == "rosetta":
        success = upload_rosetta()
    else:
        success = False
        print(f"ERROR: Unknown action '{args.action}'")
        logger.error(f"Unknown action '{args.action}'")

    return success


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
        success = _call_requested_action(parsed_arguments)
    except UserError as err:
        logger.error(f"Terminate because of this UserError: {err.message}")
        print(err.message)
        sys.exit(1)
    # let BaseError and all unexpected errors escalate, so that a stack trace is printed

    if not success:
        logger.error("Terminate without success")
        sys.exit(1)


if __name__ == "__main__":
    main()
