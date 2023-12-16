import argparse
from functools import partial
from typing import Callable

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
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import validate_xml_against_schema

logger = get_logger(__name__)


def call_requested_action(args: argparse.Namespace) -> bool:
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
    function_map: dict[str, Callable[[], bool]] = {
        "create": partial(_call_create, args),
        "xmlupload": partial(_call_xmlupload, args),
        "excel2json": partial(_call_excel2json, args),
        "excel2lists": partial(_call_excel2lists, args),
        "excel2resources": partial(_call_excel2resources, args),
        "excel2properties": partial(_call_excel2properties, args),
        "id2iri": partial(_call_id2iri, args),
        "excel2xml": partial(_call_excel2xml, args),
        "start-stack": partial(_call_start_stack, args),
        "stop-stack": _call_stop_stack,
        "get": partial(_call_get, args),
        "process-files": partial(_call_process_files, args),
        "upload-files": partial(_call_upload_files, args),
        "fast-xmlupload": partial(_call_fast_xmlupload, args),
        "template": generate_template_repo,
        "rosetta": upload_rosetta,
    }
    error_function = partial(_unknown_command, args.action)
    call_function = function_map.get(args.action, error_function)
    return call_function()


def _call_stop_stack() -> bool:
    stack_handler = StackHandler(StackConfiguration())
    return stack_handler.stop_stack()


def _call_start_stack(args: argparse.Namespace) -> bool:
    stack_handler = StackHandler(
        StackConfiguration(
            max_file_size=args.max_file_size,
            enforce_docker_system_prune=args.prune,
            suppress_docker_system_prune=args.no_prune,
            latest_dev_version=args.latest,
        )
    )
    return stack_handler.start_stack()


def _call_excel2xml(args: argparse.Namespace) -> bool:
    success, _ = excel2xml(
        datafile=args.data_source,
        shortcode=args.project_shortcode,
        default_ontology=args.ontology_name,
    )
    return success


def _call_id2iri(args: argparse.Namespace) -> bool:
    return id2iri(
        xml_file=args.xmlfile,
        json_file=args.mapping,
        remove_resource_if_id_in_mapping=args.remove_resources,
    )


def _call_excel2properties(args: argparse.Namespace) -> bool:
    _, success = excel2properties(
        excelfile=args.excelfile,
        path_to_output_file=args.properties_section,
    )
    return success


def _call_excel2resources(args: argparse.Namespace) -> bool:
    _, success = excel2resources(
        excelfile=args.excelfile,
        path_to_output_file=args.resources_section,
    )
    return success


def _call_excel2lists(args: argparse.Namespace) -> bool:
    _, success = excel2lists(
        excelfolder=args.excelfolder,
        path_to_output_file=args.lists_section,
        verbose=args.verbose,
    )
    return success


def _call_excel2json(args: argparse.Namespace) -> bool:
    return excel2json(
        data_model_files=args.excelfolder,
        path_to_output_file=args.project_definition,
    )


def _call_fast_xmlupload(args: argparse.Namespace) -> bool:
    return fast_xmlupload(
        xml_file=args.xml_file,
        user=args.user,
        password=args.password,
        dsp_url=args.server,
        sipi_url=args.sipi_url,
    )


def _call_upload_files(args: argparse.Namespace) -> bool:
    return upload_files(
        dir_with_processed_files=args.processed_dir,
        nthreads=args.nthreads,
        user=args.user,
        password=args.password,
        dsp_url=args.server,
        sipi_url=args.sipi_url,
    )


def _call_process_files(args: argparse.Namespace) -> bool:
    return process_files(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        xml_file=args.xml_file,
        nthreads=args.nthreads,
    )


def _call_xmlupload(args: argparse.Namespace) -> bool:
    if args.validate_only:
        return validate_xml_against_schema(args.xmlfile)
    else:
        return xmlupload(
            input_file=args.xmlfile,
            server=args.server,
            user=args.user,
            password=args.password,
            imgdir=args.imgdir,
            sipi=args.sipi_url,
            config=UploadConfig(diagnostics=DiagnosticsConfig(verbose=args.verbose, dump=args.dump)),
        )


def _call_get(args: argparse.Namespace) -> bool:
    return get_project(
        project_identifier=args.project,
        outfile_path=args.project_definition,
        server=args.server,
        user=args.user,
        password=args.password,
        verbose=args.verbose,
        dump=args.dump,
    )


def _call_create(args: argparse.Namespace) -> bool:
    success = False
    match args.lists_only, args.validate_only:
        case True, True:
            success = validate_lists_section_with_schema(args.project_definition)
            print("'Lists' section of the JSON project file is syntactically correct and passed validation.")
        case True, False:
            _, success = create_lists(
                project_file_as_path_or_parsed=args.project_definition,
                server=args.server,
                user=args.user,
                password=args.password,
                dump=args.dump,
            )
        case False, True:
            success = validate_project(args.project_definition)
            print("JSON project file is syntactically correct and passed validation.")
        case False, False:
            success = create_project(
                project_file_as_path_or_parsed=args.project_definition,
                server=args.server,
                user_mail=args.user,
                password=args.password,
                verbose=args.verbose,
                dump=args.dump,
            )
    return success


def _unknown_command(command: str) -> bool:
    print(f"ERROR: Unknown action '{command}'")
    logger.error(f"Unknown action '{command}'")
    return False
