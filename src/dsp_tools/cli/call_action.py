import argparse

from loguru import logger

from dsp_tools.cli.call_action_files_only import call_excel2json
from dsp_tools.cli.call_action_files_only import call_excel2lists
from dsp_tools.cli.call_action_files_only import call_excel2properties
from dsp_tools.cli.call_action_files_only import call_excel2resources
from dsp_tools.cli.call_action_files_only import call_id2iri
from dsp_tools.cli.call_action_files_only import call_old_excel2json
from dsp_tools.cli.call_action_files_only import call_old_excel2lists
from dsp_tools.cli.call_action_with_network import call_create
from dsp_tools.cli.call_action_with_network import call_get
from dsp_tools.cli.call_action_with_network import call_ingest_files
from dsp_tools.cli.call_action_with_network import call_ingest_xmlupload
from dsp_tools.cli.call_action_with_network import call_resume_xmlupload
from dsp_tools.cli.call_action_with_network import call_start_stack
from dsp_tools.cli.call_action_with_network import call_stop_stack
from dsp_tools.cli.call_action_with_network import call_upload_files
from dsp_tools.cli.call_action_with_network import call_validate_data
from dsp_tools.cli.call_action_with_network import call_xmlupload


def call_requested_action(args: argparse.Namespace) -> bool:  # noqa: PLR0912 (too many branches)
    """
    Call the appropriate function of DSP-TOOLS.

    Args:
        args: parsed CLI arguments

    Raises:
        BaseError: from the called function
        InputError: from the called function
        DockerNotReachableError: from the called function
        LocalDspApiNotReachableError: from the called function
        unexpected errors from the called methods and underlying libraries

    Returns:
        success status
    """
    match args.action:
        # commands with Docker / API interactions
        case "start-stack":
            result = call_start_stack(args)
        case "stop-stack":
            result = call_stop_stack()
        case "create":
            result = call_create(args)
        case "get":
            result = call_get(args)
        case "validate-data":
            result = call_validate_data(args)
        case "xmlupload":
            result = call_xmlupload(args)
        case "resume-xmlupload":
            result = call_resume_xmlupload(args)
        case "upload-files":
            result = call_upload_files(args)
        case "ingest-files":
            result = call_ingest_files(args)
        case "ingest-xmlupload":
            result = call_ingest_xmlupload(args)
        # commands that do not require docker
        case "excel2json":
            result = call_excel2json(args)
        case "old-excel2json":
            result = call_old_excel2json(args)
        case "excel2lists":
            result = call_excel2lists(args)
        case "old-excel2lists":
            result = call_old_excel2lists(args)
        case "excel2resources":
            result = call_excel2resources(args)
        case "excel2properties":
            result = call_excel2properties(args)
        case "id2iri":
            result = call_id2iri(args)
        case _:
            print(f"ERROR: Unknown action '{args.action}'")
            logger.error(f"Unknown action '{args.action}'")
            result = False
    return result
