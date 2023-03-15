"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import datetime
import sys
from importlib.metadata import version

from dsp_tools.excel2xml import excel2xml
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.excel_to_json_lists import excel2lists, validate_lists_section_with_schema
from dsp_tools.utils.excel_to_json_project import excel2json
from dsp_tools.utils.excel_to_json_properties import excel2properties
from dsp_tools.utils.excel_to_json_resources import excel2resources
from dsp_tools.utils.id_to_iri import id_to_iri
from dsp_tools.utils.project_create_lists import create_lists
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.project_get import get_project
from dsp_tools.utils.project_validate import validate_project
from dsp_tools.utils.shared import validate_xml_against_schema
from dsp_tools.utils.stack_handling import start_stack, stop_stack
from dsp_tools.utils.xml_upload import xml_upload
from dsp_tools.utils.xml_upload_enhanced import generate_testdata, enhanced_xml_upload


def make_parser() -> argparse.ArgumentParser:
    """
    Create a parser for the command line arguments

    Returns:
        parser
    """
    # help texts
    username_text = "username (e-mail) used for authentication with the DSP-API "
    password_text = "password used for authentication with the DSP-API "
    remote_dsp_api_server_text = "URL of the DSP server"
    verbose_text = "print more information about the progress to the console"

    # default values
    default_dsp_api_url = "http://0.0.0.0:3333"
    default_user = "root@example.com"
    default_pw = "test"

    # make a parser
    parser = argparse.ArgumentParser(description=f"DSP-TOOLS (version {version('dsp-tools')}, © {datetime.datetime.now().year} by DaSCH)")
    subparsers = parser.add_subparsers(title="Subcommands", description="Valid subcommands are", help="sub-command help")

    # create
    parser_create = subparsers.add_parser(
        name="create", 
        help="Create a project defined in a JSON project file on a DSP server. "
             "A project can consist of lists, groups, users, and ontologies (data models)."
    )
    parser_create.set_defaults(action="create")
    parser_create.add_argument("-s", "--server", default=default_dsp_api_url, help=remote_dsp_api_server_text)
    parser_create.add_argument("-u", "--user", default=default_user, help=username_text)
    parser_create.add_argument("-p", "--password", default=default_pw, help=password_text)
    parser_create.add_argument("-V", "--validate-only", action="store_true", 
                               help="validate the JSON file without creating it on the DSP server")
    parser_create.add_argument("-l", "--lists-only", action="store_true", help="create only the lists (prerequisite: the project exists on the server)")
    parser_create.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_create.add_argument("-d", "--dump", action="store_true", help="dump test files for DSP-API requests")
    parser_create.add_argument("project_definition", help="path to the JSON project file")

    # get
    parser_get = subparsers.add_parser(name="get", help="Retrieve a project with its data model(s) from a DSP server and write it into a JSON file")
    parser_get.set_defaults(action="get")
    parser_get.add_argument("-s", "--server", default=default_dsp_api_url, help=remote_dsp_api_server_text)
    parser_get.add_argument("-u", "--user", default=default_user, help=username_text)
    parser_get.add_argument("-p", "--password", default=default_pw, help=password_text)
    parser_get.add_argument("-P", "--project", help="shortcode, shortname or IRI of the project", required=True)
    parser_get.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_get.add_argument("project_definition", help="path to the file the project should be written to")

    # xmlupload
    parser_upload = subparsers.add_parser(name="xmlupload", help="Upload data defined in an XML file to a DSP server")
    parser_upload.set_defaults(action="xmlupload")
    parser_upload.add_argument("-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to")
    parser_upload.add_argument("-u", "--user", default=default_user, help=username_text)
    parser_upload.add_argument("-p", "--password", default=default_pw, help=password_text)
    parser_upload.add_argument("-S", "--sipi", default="http://0.0.0.0:1024", help="URL of the SIPI server where DSP-TOOLS sends the multimedia files to")
    parser_upload.add_argument("-i", "--imgdir", default=".", help="folder from where the paths in the <bitstream> tags are evaluated")
    parser_upload.add_argument("-I", "--incremental", action="store_true", 
                               help="The links in the XML file point to IRIs (on the server) instead of IDs (in the same XML file).")
    parser_upload.add_argument("-V", "--validate", action="store_true", help="validate the XML file without uploading it")
    parser_upload.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_upload.add_argument("-m", "--metrics", action="store_true", help="write metrics into a 'metrics' folder")
    parser_upload.add_argument("xmlfile", help="path to the XML file containing the data")

    # enhanced-xmlupload
    parser_enhanced_xmlupload = subparsers.add_parser(
        name="enhanced-xmlupload",
        help="For internal use only: Upload data from an XML file to the DaSCH Service Platform. Preprocess the data locally first."
    )
    parser_enhanced_xmlupload.set_defaults(action="enhanced-xmlupload")
    parser_enhanced_xmlupload.add_argument("--multimedia-folder", default="multimedia", help="Path to folder containing the multimedia files")
    parser_enhanced_xmlupload.add_argument("--local-sipi-server", default="http://0.0.0.0:1024", help="URL of the local SIPI IIIF server")
    parser_enhanced_xmlupload.add_argument("--sipi-processed-path", help="Path to folder containing the processed multimedia files")
    parser_enhanced_xmlupload.add_argument("--generate-test-data", action="store_true", help="only generate a test data folder in the current working directory (no upload)")
    parser_enhanced_xmlupload.add_argument("--size", default="small", help="size of test data set: small/medium/big")
    parser_enhanced_xmlupload.add_argument("-s", "--remote-dsp-server", default=default_dsp_api_url, help=remote_dsp_api_server_text)
    parser_enhanced_xmlupload.add_argument("-S", "--remote-sipi-server", default="http://0.0.0.0:1024", help="URL of the remote SIPI IIIF server (for testing purposes, can be the same as `--local-sipi-server`)")
    parser_enhanced_xmlupload.add_argument("-t", "--num-of-threads-for-processing", type=int, default=8, help="number of threads used for sending requests to the local SIPI")
    parser_enhanced_xmlupload.add_argument("-T", "--num-of-threads-for-uploading", type=int, default=4, help="number of threads used for uploading the preprocessed files to the remote SIPI")
    parser_enhanced_xmlupload.add_argument("-u", "--user", default=default_user, help=username_text)
    parser_enhanced_xmlupload.add_argument("-p", "--password", default=default_pw, help=password_text)
    parser_enhanced_xmlupload.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_enhanced_xmlupload.add_argument("-I", "--incremental", action="store_true", help="Incremental XML upload")
    parser_enhanced_xmlupload.add_argument("xmlfile", help="path to xml file containing the data")

    # excel2json
    parser_excel2json = subparsers.add_parser(
        name="excel2json",
        help="Create an entire JSON project file from a folder containing the required Excel files"
    )
    parser_excel2json.set_defaults(action="excel2json")
    parser_excel2json.add_argument("excelfolder", help="path to the folder containing the Excel files")
    parser_excel2json.add_argument("project_definition", help="path to the output JSON file")

    # excel2lists
    parser_excel_lists = subparsers.add_parser(
        name="excel2lists",
        help="Create the 'lists' section of a JSON project file from one or multiple Excel files"
    )
    parser_excel_lists.set_defaults(action="excel2lists")
    parser_excel_lists.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_excel_lists.add_argument("excelfolder", help="path to the folder containing the Excel file(s)")
    parser_excel_lists.add_argument("lists_section", help="path to the output JSON file containing the 'lists' section")

    # excel2resources
    parser_excel_resources = subparsers.add_parser(
        name="excel2resources", 
        help="Create the 'resources' section of a JSON project file from one or multiple Excel files"
    )
    parser_excel_resources.set_defaults(action="excel2resources")
    parser_excel_resources.add_argument("excelfile", help="path to the Excel file containing the resources")
    parser_excel_resources.add_argument("resources_section", help="path to the output JSON file containing the 'resources' section")

    # excel2properties
    parser_excel_properties = subparsers.add_parser(
        name="excel2properties", 
        help="Create the 'properties' section of a JSON project file from one or multiple Excel files"
    )
    parser_excel_properties.set_defaults(action="excel2properties")
    parser_excel_properties.add_argument("excelfile", help="path to the Excel file containing the properties")
    parser_excel_properties.add_argument("properties_section", help="path to the output JSON file containing the 'properties' section")

    # excel2xml
    parser_excel2xml = subparsers.add_parser(
        name="excel2xml", 
        help="Create an XML file from an Excel/CSV file that is already structured according to the DSP specifications"
    )
    parser_excel2xml.set_defaults(action="excel2xml")
    parser_excel2xml.add_argument("data_source", help="path to the CSV or XLS(X) file containing the data")
    parser_excel2xml.add_argument("project_shortcode", help="shortcode of the project that this data belongs to")
    parser_excel2xml.add_argument("ontology_name", help="name of the ontology that this data belongs to")

    # id2iri
    parser_id2iri = subparsers.add_parser(
        name="id2iri", 
        help="Replace internal IDs in contained in the <resptr> tags of an XML file by IRIs provided in a mapping file"
    )
    parser_id2iri.set_defaults(action="id2iri")
    parser_id2iri.add_argument("--outfile", help="path to the XML output file containing the replaced IDs")
    parser_id2iri.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    parser_id2iri.add_argument("xmlfile", help="path to the XML file containing the data to be replaced")
    parser_id2iri.add_argument("mapping", help="path to the JSON file containing the mapping of IDs to IRIs")

    # startup DSP stack
    parser_stackup = subparsers.add_parser(name="start-stack", help="Run a local instance of DSP-API and DSP-APP")
    parser_stackup.set_defaults(action="start-stack")
    parser_stackup.add_argument("--max_file_size", type=int, 
                                help="max. multimedia file size allowed by SIPI, in MB (default: 250, max: 100'000)")
    parser_stackup.add_argument("--prune", action="store_true", help="execute 'docker system prune' without asking")
    parser_stackup.add_argument("--no-prune", action="store_true", help="don't execute 'docker system prune' (and don't ask)")

    # shutdown DSP-API
    parser_stackdown = subparsers.add_parser(
        name="stop-stack", 
        help="Shut down the local instance of DSP-API and DSP-APP, and delete all data in it"
    )
    parser_stackdown.set_defaults(action="stop-stack")

    return parser


def call_requested_action(
    user_args: list[str], 
    parser: argparse.ArgumentParser
) -> bool:
    """
    With the help of the parser, parse the user arguments and call the appropriate method of DSP-TOOLS.

    Args:
        user_args: list of arguments passed by the user from the command line
        parser: parser to parse the user arguments

    Raises:
        BaseError from the called methods
        UserError from the called methods
        unexpected errors from the called methods and underlying libraries
    
    Returns:
        success status
    """
    args = parser.parse_args(user_args)
    if not hasattr(args, "action"):
        parser.print_help(sys.stderr)
        exit(1)
    elif args.action == "create":
        if args.lists_only:
            if args.validate_only:
                success = validate_lists_section_with_schema(path_to_json_project_file=args.project_definition)
                print("'Lists' section of the JSON project file is syntactically correct and passed validation.")
            else:
                _, success = create_lists(
                    project_file_as_path_or_parsed=args.project_definition,
                    server=args.server,
                    user=args.user,
                    password=args.password,
                    dump=args.dump
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
                    dump=args.dump
                )
    elif args.action == "get":
        success = get_project(
            project_identifier=args.project,
            outfile_path=args.project_definition,
            server=args.server,
            user=args.user,
            password=args.password,
            verbose=args.verbose
        )
    elif args.action == "xmlupload":
        if args.validate:
            success = validate_xml_against_schema(input_file=args.xmlfile)
        else:
            success = xml_upload(
                input_file=args.xmlfile,
                server=args.server,
                user=args.user,
                password=args.password,
                imgdir=args.imgdir,
                sipi=args.sipi,
                verbose=args.verbose,
                incremental=args.incremental,
                save_metrics=args.metrics,
                preprocessing_done=False
    elif args.action == "enhanced-xmlupload":
        if args.generate_test_data:
            success = generate_testdata(size=args.size)
        else:
            success = enhanced_xml_upload(
                local_sipi_server=args.local_sipi_server,
                sipi_processed_path=args.sipi_processed_path,
                remote_dsp_server=args.remote_dsp_server,
                remote_sipi_server=args.remote_sipi_server,
                processing_threads=args.num_of_threads_for_processing,
                uploading_threads=args.num_of_threads_for_uploading,
                user=args.user,
                password=args.password,
                xmlfile=args.xmlfile,
                verbose=args.verbose,
                incremental=args.incremental
            )
    elif args.action == "excel2json":
        success = excel2json(
            data_model_files=args.excelfolder,
            path_to_output_file=args.project_definition
        )
    elif args.action == "excel2lists":
        _, success = excel2lists(
            excelfolder=args.excelfolder,
            path_to_output_file=args.lists_section,
            verbose=args.verbose
        )
    elif args.action == "excel2resources":
        _, success = excel2resources(
            excelfile=args.excelfile,
            path_to_output_file=args.resources_section
        )
    elif args.action == "excel2properties":
        _, success = excel2properties(
            excelfile=args.excelfile,
            path_to_output_file=args.properties_section
        )
    elif args.action == "id2iri":
        success = id_to_iri(
            xml_file=args.xmlfile,
            json_file=args.mapping,
            out_file=args.outfile,
            verbose=args.verbose
        )
    elif args.action == "excel2xml":
        success = excel2xml(
            datafile=args.data_source,
            shortcode=args.project_shortcode,
            default_ontology=args.ontology_name
        )
    elif args.action == "start-stack":
        success = start_stack(
            max_file_size=args.max_file_size,
            enforce_docker_system_prune=args.prune,
            suppress_docker_system_prune=args.no_prune
        )
    elif args.action == "stop-stack":
        success = stop_stack()
    else:
        success = False

    return success
    


def main() -> None:
    """Main entry point of the program as referenced in pyproject.toml"""
    parser = make_parser()
    try:
        success = call_requested_action(user_args=sys.argv[1:], parser=parser)
    except UserError as err:
        print(err.message)
        exit(1)
    # let BaseError and all unexpected errors escalate, so that a stack trace is printed

    if not success: 
        exit(1)

if __name__ == "__main__":
    main()
