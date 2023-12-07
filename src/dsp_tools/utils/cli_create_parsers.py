import argparse
import datetime
from importlib.metadata import version

# help texts
username_text = "username (e-mail) used for authentication with the DSP-API"
password_text = "password used for authentication with the DSP-API"
dsp_server_text = "URL of the DSP server"
verbose_text = "print more information about the progress to the console"


def make_parser(
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

    # make a parser
    parser = argparse.ArgumentParser(
        description=f"DSP-TOOLS (version {version('dsp-tools')}, © {datetime.datetime.now().year} by DaSCH)"
    )
    subparsers = parser.add_subparsers(
        title="Subcommands", description="Valid subcommands are", help="sub-command help"
    )

    _for_start_stack(subparsers)

    _for_stop_stack(subparsers)

    _for_create(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _for_get(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _for_xmlupload(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _for_fast_xmlupload(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _for_process_files(subparsers)

    _for_upload_files(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _for_excel2json(subparsers)

    _for_excel2lists(subparsers)

    _for_excel2resources(subparsers)

    _for_excel2properties(subparsers)

    _for_excel2xml(subparsers)

    _for_id2iri(subparsers)

    _for_create_template(subparsers)

    _for_rosetta(subparsers)

    return parser


def _for_rosetta(subparsers):
    subparsers = subparsers.add_parser(
        name="rosetta", help="Clone the most up to data rosetta repository, create the data model and upload the data"
    )
    subparsers.set_defaults(action="rosetta")


def _for_create_template(subparsers):
    # create template repo with minimal JSON and XML files
    subparsers = subparsers.add_parser(
        name="template", help="Create a template repository with a minimal JSON and XML file"
    )
    subparsers.set_defaults(action="template")


def _for_stop_stack(subparsers):
    subparsers = subparsers.add_parser(
        name="stop-stack", help="Shut down the local instance of DSP-API and DSP-APP, and delete all data in it"
    )
    subparsers.set_defaults(action="stop-stack")


def _for_start_stack(subparsers):
    subparsers = subparsers.add_parser(name="start-stack", help="Run a local instance of DSP-API and DSP-APP")
    subparsers.set_defaults(action="start-stack")
    subparsers.add_argument(
        "--max_file_size",
        type=int,
        help="max. multimedia file size allowed by SIPI, in MB (default: 250, max: 100'000)",
    )
    subparsers.add_argument("--prune", action="store_true", help="execute 'docker system prune' without asking")
    subparsers.add_argument(
        "--no-prune", action="store_true", help="don't execute 'docker system prune' (and don't ask)"
    )
    subparsers.add_argument(
        "--latest",
        action="store_true",
        help="use the latest dev version of DSP-API, from the main branch of the GitHub repository",
    )


def _for_id2iri(subparsers):
    subparsers = subparsers.add_parser(
        name="id2iri",
        help="Replace internal IDs of an XML file (resptr tags or salsah-links) by IRIs provided in a mapping file.",
    )
    subparsers.set_defaults(action="id2iri")
    subparsers.add_argument(
        "-r", "--remove-resources", action="store_true", help="remove resources if their ID is in the mapping"
    )
    subparsers.add_argument("xmlfile", help="path to the XML file containing the data to be replaced")
    subparsers.add_argument("mapping", help="path to the JSON file containing the mapping of IDs to IRIs")


def _for_excel2xml(subparsers):
    subparsers = subparsers.add_parser(
        name="excel2xml",
        help="Create an XML file from an Excel/CSV file that is already structured according to the DSP specifications",
    )
    subparsers.set_defaults(action="excel2xml")
    subparsers.add_argument("data_source", help="path to the CSV or XLS(X) file containing the data")
    subparsers.add_argument("project_shortcode", help="shortcode of the project that this data belongs to")
    subparsers.add_argument("ontology_name", help="name of the ontology that this data belongs to")


def _for_excel2properties(subparsers):
    subparsers = subparsers.add_parser(
        name="excel2properties",
        help="Create the 'properties' section of a JSON project file from one or multiple Excel files",
    )
    subparsers.set_defaults(action="excel2properties")
    subparsers.add_argument("excelfile", help="path to the Excel file containing the properties")
    subparsers.add_argument(
        "properties_section", help="path to the output JSON file containing the 'properties' section"
    )


def _for_excel2resources(subparsers):
    subparsers = subparsers.add_parser(
        name="excel2resources",
        help="Create the 'resources' section of a JSON project file from one or multiple Excel files",
    )
    subparsers.set_defaults(action="excel2resources")
    subparsers.add_argument("excelfile", help="path to the Excel file containing the resources")
    subparsers.add_argument("resources_section", help="path to the output JSON file containing the 'resources' section")


def _for_excel2lists(subparsers):
    subparsers = subparsers.add_parser(
        name="excel2lists",
        help="Create the 'lists' section of a JSON project file from one or multiple Excel files",
    )
    subparsers.set_defaults(action="excel2lists")
    subparsers.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparsers.add_argument("excelfolder", help="path to the folder containing the Excel file(s)")
    subparsers.add_argument("lists_section", help="path to the output JSON file containing the 'lists' section")


def _for_excel2json(subparsers):
    subparsers = subparsers.add_parser(
        name="excel2json",
        help="Create an entire JSON project file from a folder containing the required Excel files",
    )
    subparsers.set_defaults(action="excel2json")
    subparsers.add_argument("excelfolder", help="path to the folder containing the Excel files")
    subparsers.add_argument("project_definition", help="path to the output JSON file")


def _for_fast_xmlupload(subparsers, default_dsp_api_url: str, root_user_email: str, root_user_pw: str):
    subparsers = subparsers.add_parser(
        name="fast-xmlupload",
        help="For internal use only: create resources with already uploaded files",
    )
    subparsers.set_defaults(action="fast-xmlupload")
    subparsers.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparsers.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparsers.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparsers.add_argument("xml_file", help="path to XML file containing the data")


def _for_upload_files(subparsers, default_dsp_api_url: str, root_user_email: str, root_user_pw: str):
    subparsers = subparsers.add_parser(
        name="upload-files",
        help="For internal use only: upload already processed files",
    )
    subparsers.set_defaults(action="upload-files")
    subparsers.add_argument("-d", "--processed-dir", help="path to the directory with the processed files")
    subparsers.add_argument("-n", "--nthreads", type=int, default=4, help="number of threads to use")
    subparsers.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparsers.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparsers.add_argument("-p", "--password", default=root_user_pw, help=password_text)


def _for_process_files(subparsers):
    subparsers = subparsers.add_parser(
        name="process-files",
        help="For internal use only: process all files referenced in an XML file",
    )
    subparsers.set_defaults(action="process-files")
    subparsers.add_argument("--input-dir", help="path to the input directory where the files should be read from")
    subparsers.add_argument(
        "--output-dir", help="path to the output directory where the processed/transformed files should be written to"
    )
    subparsers.add_argument("--nthreads", type=int, default=None, help="number of threads to use")
    subparsers.add_argument("xml_file", help="path to XML file containing the data")


def _for_xmlupload(subparsers, default_dsp_api_url: str, root_user_email: str, root_user_pw: str):
    subparsers = subparsers.add_parser(name="xmlupload", help="Upload data defined in an XML file to a DSP server")
    subparsers.set_defaults(action="xmlupload")
    subparsers.add_argument(
        "-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to"
    )
    subparsers.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparsers.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparsers.add_argument(
        "-i", "--imgdir", default=".", help="folder from where the paths in the <bitstream> tags are evaluated"
    )
    subparsers.add_argument(
        "-V", "--validate-only", action="store_true", help="validate the XML file without uploading it"
    )
    subparsers.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparsers.add_argument("-d", "--dump", action="store_true", help="write every request to DSP-API/SIPI into a file")
    subparsers.add_argument("xmlfile", help="path to the XML file containing the data")


def _for_get(subparsers, default_dsp_api_url: str, root_user_email: str, root_user_pw: str):
    subparsers = subparsers.add_parser(
        name="get",
        help="Retrieve a project with its data model(s) from a DSP server and write it into a JSON file",
    )
    subparsers.set_defaults(action="get")
    subparsers.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparsers.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparsers.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparsers.add_argument("-P", "--project", help="shortcode, shortname or IRI of the project", required=True)
    subparsers.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparsers.add_argument("-d", "--dump", action="store_true", help="write every request to DSP-API into a file")
    subparsers.add_argument("project_definition", help="path to the file the project should be written to")


def _for_create(subparsers, default_dsp_api_url: str, root_user_email: str, root_user_pw: str):
    subparsers = subparsers.add_parser(
        name="create",
        help="Create a project defined in a JSON project file on a DSP server. "
        "A project can consist of lists, groups, users, and ontologies (data models).",
    )
    subparsers.set_defaults(action="create")
    subparsers.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparsers.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparsers.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparsers.add_argument(
        "-V",
        "--validate-only",
        action="store_true",
        help="validate the JSON file without creating it on the DSP server",
    )
    subparsers.add_argument(
        "-l",
        "--lists-only",
        action="store_true",
        help="create only the lists (prerequisite: the project exists on the server)",
    )
    subparsers.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparsers.add_argument("-d", "--dump", action="store_true", help="write every request to DSP-API into a file")
    subparsers.add_argument("project_definition", help="path to the JSON project file")
