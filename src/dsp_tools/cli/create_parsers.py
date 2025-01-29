from __future__ import annotations

import datetime
from argparse import ArgumentParser
from argparse import _SubParsersAction
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
) -> ArgumentParser:
    """
    Create a parser for the command line arguments.

    Args:
        default_dsp_api_url: URL of the DSP server (default value for localhost)
        root_user_email: username (e-mail) used for authentication with the DSP-API (default value for localhost)
        root_user_pw: password used for authentication with the DSP-API (default value for localhost)

    Returns:
        parser
    """

    parser = ArgumentParser(
        description=f"DSP-TOOLS (version {version('dsp-tools')}, © {datetime.datetime.now().year} by DaSCH)"
    )
    subparsers = parser.add_subparsers(
        title="Subcommands", description="Valid subcommands are", help="sub-command help"
    )

    _add_start_stack(subparsers)

    _add_stop_stack(subparsers)

    _add_create(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _add_get(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _add_xmlupload(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _add_validate_data(subparsers, default_dsp_api_url)

    _add_resume_xmlupload(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _add_upload_files(subparsers, default_dsp_api_url, root_user_email, root_user_pw)
    _add_ingest_files(subparsers, default_dsp_api_url, root_user_email, root_user_pw)
    _add_ingest_xmlupload(subparsers, default_dsp_api_url, root_user_email, root_user_pw)

    _add_new_excel2json(subparsers)
    _add_excel2json(subparsers)

    _add_new_excel2lists(subparsers)
    _add_excel2lists(subparsers)

    _add_excel2resources(subparsers)

    _add_excel2properties(subparsers)

    _add_excel2xml(subparsers)

    _add_id2iri(subparsers)

    _add_create_template(subparsers)

    _add_rosetta(subparsers)

    _add_suppress_update_prompt(subparsers)

    return parser


def _add_suppress_update_prompt(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    outdated_help_text = (
        "don't prompt when using an outdated version of DSP-TOOLS "
        "(useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)"
    )
    for sp in subparsers.choices.values():
        sp.add_argument("--suppress-update-prompt", action="store_true", help=outdated_help_text)


def _add_rosetta(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="rosetta", help="Clone the most up to data rosetta repository, create the data model and upload the data"
    )
    subparser.set_defaults(action="rosetta")


def _add_create_template(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    # create template repo with minimal JSON and XML files
    subparser = subparsers.add_parser(
        name="template", help="Create a template repository with a minimal JSON and XML file"
    )
    subparser.set_defaults(action="template")


def _add_stop_stack(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="stop-stack", help="Shut down the local instance of DSP-API and DSP-APP, and delete all data in it"
    )
    subparser.set_defaults(action="stop-stack")


def _add_start_stack(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    latest_text = (
        "instead of the latest deployed version, "
        "use the latest development version (from the `main` branch) "
        "of the backend components (api, sipi, fuseki, ingest)"
    )
    max_file_size_text = "max. multimedia file size allowed for ingest, in MB (default: 2000, max: 100'000)"
    no_prune_text = "don't execute 'docker system prune' (and don't ask)"
    with_test_data_text = "initialise the database with built-in test data"
    subparser = subparsers.add_parser(name="start-stack", help="Run a local instance of DSP-API and DSP-APP")
    subparser.set_defaults(action="start-stack")
    subparser.add_argument("--max_file_size", type=int, help=max_file_size_text)
    subparser.add_argument("--prune", action="store_true", help="execute 'docker system prune' without asking")
    subparser.add_argument("--no-prune", action="store_true", help=no_prune_text)
    subparser.add_argument("--latest", action="store_true", help=latest_text)
    subparser.add_argument("--with-test-data", action="store_true", help=with_test_data_text)
    subparser.add_argument("--validation", action="store_true")


def _add_id2iri(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="id2iri",
        help="Replace internal IDs of an XML file (resptr tags or salsah-links) by IRIs provided in a mapping file.",
    )
    subparser.set_defaults(action="id2iri")
    subparser.add_argument(
        "-r", "--remove-resources", action="store_true", help="remove resources if their ID is in the mapping"
    )
    subparser.add_argument("xmlfile", help="path to the XML file containing the data to be replaced")
    subparser.add_argument("mapping", help="path to the JSON file containing the mapping of IDs to IRIs")


def _add_excel2xml(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="excel2xml",
        help="Create an XML file from an Excel/CSV file that is already structured according to the DSP specifications",
    )
    subparser.set_defaults(action="excel2xml")
    subparser.add_argument("data_source", help="path to the CSV or XLS(X) file containing the data")
    subparser.add_argument("project_shortcode", help="shortcode of the project that this data belongs to")
    subparser.add_argument("ontology_name", help="name of the ontology that this data belongs to")


def _add_excel2properties(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="excel2properties",
        help="Create the 'properties' section of a JSON project file from one or multiple Excel files",
    )
    subparser.set_defaults(action="excel2properties")
    subparser.add_argument("excelfile", help="path to the Excel file containing the properties")
    subparser.add_argument(
        "properties_section", help="path to the output JSON file containing the 'properties' section"
    )


def _add_excel2resources(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="excel2resources",
        help="Create the 'resources' section of a JSON project file from one or multiple Excel files",
    )
    subparser.set_defaults(action="excel2resources")
    subparser.add_argument("excelfile", help="path to the Excel file containing the resources")
    subparser.add_argument("resources_section", help="path to the output JSON file containing the 'resources' section")


def _add_new_excel2lists(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="new-excel2lists",
        help="Create the 'lists' section of a JSON project file from one or multiple Excel files",
    )
    subparser.set_defaults(action="new-excel2lists")
    subparser.add_argument("excelfolder", help="path to the folder containing the Excel file(s)")
    subparser.add_argument("lists_section", help="path to the output JSON file containing the 'lists' section")


def _add_excel2lists(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="excel2lists",
        help="Create the 'lists' section of a JSON project file from one or multiple Excel files",
    )
    subparser.set_defaults(action="excel2lists")
    subparser.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparser.add_argument("excelfolder", help="path to the folder containing the Excel file(s)")
    subparser.add_argument("lists_section", help="path to the output JSON file containing the 'lists' section")


def _add_excel2json(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="excel2json",
        help="Create an entire JSON project file from a folder containing the required Excel files",
    )
    subparser.set_defaults(action="excel2json")
    subparser.add_argument("excelfolder", help="path to the folder containing the Excel files")
    subparser.add_argument("project_definition", help="path to the output JSON file")


def _add_new_excel2json(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    subparser = subparsers.add_parser(
        name="new-excel2json",
        help="Create an entire JSON project file from a folder containing the required Excel files",
    )
    subparser.set_defaults(action="new-excel2json")
    subparser.add_argument("excelfolder", help="path to the folder containing the Excel files")
    subparser.add_argument("project_definition", help="path to the output JSON file")


def _add_upload_files(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(
        name="upload-files",
        help="Experimental: upload all files referenced in an XML file to a DSP server",
    )
    subparser.set_defaults(action="upload-files")
    subparser.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument(
        "-i", "--imgdir", default=".", help="folder from where the paths in the <bitstream> tags are evaluated"
    )
    subparser.add_argument("xml_file", help="path to XML file containing the data")


def _add_ingest_files(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(
        name="ingest-files",
        help="Experimental: ingest uploaded files on a DSP server and retrieve the mapping CSV file",
    )
    subparser.set_defaults(action="ingest-files")
    subparser.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument("shortcode", help="shortcode of the project that the files belong to")


def _add_ingest_xmlupload(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(
        name="ingest-xmlupload",
        help="For internal use only: create resources with files already uploaded through dsp-ingest",
    )
    subparser.set_defaults(action="ingest-xmlupload")
    subparser.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument("--interrupt-after", type=int, default=-1, help="interrupt after this number of resources")
    subparser.add_argument("xml_file", help="path to XML file containing the data")


def _add_xmlupload(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(name="xmlupload", help="Upload data defined in an XML file to a DSP server")
    subparser.set_defaults(action="xmlupload")
    subparser.add_argument(
        "-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to"
    )
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument(
        "-i", "--imgdir", default=".", help="folder from where the paths in the <bitstream> tags are evaluated"
    )
    subparser.add_argument(
        "-V", "--validate-only", action="store_true", help="validate the XML file without uploading it"
    )
    subparser.add_argument("--interrupt-after", type=int, default=-1, help="interrupt after this number of resources")
    subparser.add_argument("xmlfile", help="path to the XML file containing the data")
    subparser.add_argument("--no-iiif-uri-validation", action="store_true", help="skip the IIIF URI validation")


def _add_validate_data(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
) -> None:
    subparser = subparsers.add_parser(name="validate-data", help="Validate the data with the data model.")
    subparser.set_defaults(action="validate-data")
    subparser.add_argument("xmlfile", help="path to the XML file containing the data")
    subparser.add_argument(
        "-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to"
    )
    subparser.add_argument("--dev", action="store_true", help="Validate with experimental features.")
    subparser.add_argument(
        "--save-graphs", action="store_true", help="Save the data, onto and shacl graph as ttl files."
    )


def _add_resume_xmlupload(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(name="resume-xmlupload", help="Resume an interrupted xmlupload")
    subparser.set_defaults(action="resume-xmlupload")
    subparser.add_argument(
        "-s", "--server", default=default_dsp_api_url, help="URL of the DSP server where DSP-TOOLS sends the data to"
    )
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    skip_text = (
        "In case the last resource was successfully uploaded to the DSP-API, "
        "but DSP-TOOLS did not get a confirmation from the DSP-API, "
        "the resource will remain in the pending upload list.\n"
        "If this flag is set, the first resource in the list is skipped."
    )
    subparser.add_argument("--skip-first-resource", action="store_true", help=skip_text)


def _add_get(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(
        name="get",
        help="Retrieve a project with its data model(s) from a DSP server and write it into a JSON file",
    )
    subparser.set_defaults(action="get")
    subparser.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument("-P", "--project", help="shortcode, shortname or IRI of the project", required=True)
    subparser.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparser.add_argument("project_definition", help="path to the file the project should be written to")


def _add_create(
    subparsers: _SubParsersAction[ArgumentParser],
    default_dsp_api_url: str,
    root_user_email: str,
    root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(
        name="create",
        help="Create a project defined in a JSON project file on a DSP server. "
        "A project can consist of lists, groups, users, and ontologies (data models).",
    )
    subparser.set_defaults(action="create")
    subparser.add_argument("-s", "--server", default=default_dsp_api_url, help=dsp_server_text)
    subparser.add_argument("-u", "--user", default=root_user_email, help=username_text)
    subparser.add_argument("-p", "--password", default=root_user_pw, help=password_text)
    subparser.add_argument(
        "-V",
        "--validate-only",
        action="store_true",
        help="validate the JSON file without creating it on the DSP server",
    )
    subparser.add_argument(
        "-l",
        "--lists-only",
        action="store_true",
        help="create only the lists (prerequisite: the project exists on the server)",
    )
    subparser.add_argument("-v", "--verbose", action="store_true", help=verbose_text)
    subparser.add_argument("project_definition", help="path to the JSON project file")
