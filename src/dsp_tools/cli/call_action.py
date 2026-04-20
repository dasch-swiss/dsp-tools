import argparse

from loguru import logger

from dsp_tools.cli.call_action_files_only import call_excel2json
from dsp_tools.cli.call_action_files_only import call_excel2lists
from dsp_tools.cli.call_action_files_only import call_excel2properties
from dsp_tools.cli.call_action_files_only import call_excel2resources
from dsp_tools.cli.call_action_files_only import call_id2iri
from dsp_tools.cli.call_action_files_only import call_mapping_config
from dsp_tools.cli.call_action_files_only import call_migration_config
from dsp_tools.cli.call_action_files_only import call_old_excel2json
from dsp_tools.cli.call_action_files_only import call_old_excel2lists
from dsp_tools.cli.call_action_files_only import call_update_legal
from dsp_tools.cli.call_action_with_network import call_create
from dsp_tools.cli.call_action_with_network import call_get
from dsp_tools.cli.call_action_with_network import call_ingest_files
from dsp_tools.cli.call_action_with_network import call_ingest_xmlupload
from dsp_tools.cli.call_action_with_network import call_mapping_add
from dsp_tools.cli.call_action_with_network import call_migration_clean_up
from dsp_tools.cli.call_action_with_network import call_migration_complete
from dsp_tools.cli.call_action_with_network import call_migration_export
from dsp_tools.cli.call_action_with_network import call_migration_import
from dsp_tools.cli.call_action_with_network import call_resume_xmlupload
from dsp_tools.cli.call_action_with_network import call_start_stack
from dsp_tools.cli.call_action_with_network import call_stop_stack
from dsp_tools.cli.call_action_with_network import call_upload_files
from dsp_tools.cli.call_action_with_network import call_validate_data
from dsp_tools.cli.call_action_with_network import call_xmlupload
from dsp_tools.cli.exceptions import CliCommandNotInvokableError


def call_requested_action(args: argparse.Namespace) -> bool:  # noqa: PLR0912,PLR0915 (too many branches & too many statements)
    """
    Call the appropriate function of DSP-TOOLS.

    Args:
        args: parsed CLI arguments

    Raises:
        BaseError: from the called function
        InputError: from the called function
        DockerNotReachableError: from the called function
        DspApiNotReachableError: from the called function
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
        case "update-legal":
            result = call_update_legal(args)
        case "mapping":
            raise CliCommandNotInvokableError(
                "The command `mapping` cannot be used as a stand-alone command. "
                "Use `dsp-tools mapping --help` for available sub-commands."
            )
        case "mapping config":
            result = call_mapping_config(args)
        case "mapping add":
            result = call_mapping_add(args)
        case "migration":
            raise CliCommandNotInvokableError(
                "The command `migration` cannot be used as a stand-alone command. "
                "It can only be used with one of its subcommands. "
                "Type `dsp-tools migration --help` for a list of options."
            )
        case "migration config":
            result = call_migration_config(args)
        case "migration complete":
            result = call_migration_complete(args)
        case "migration export":
            result = call_migration_export(args)
        case "migration import":
            result = call_migration_import(args)
        case "migration clean-up":
            result = call_migration_clean_up(args)
        case _:
            print(f"ERROR: Unknown action '{args.action}'")
            logger.error(f"Unknown action '{args.action}'")
            result = False
    return result
