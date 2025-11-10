import argparse
from pathlib import Path

from dsp_tools.cli.args import NetworkRequirements
from dsp_tools.cli.args import PathDependencies
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.cli.utils import check_docker_health
from dsp_tools.cli.utils import check_input_dependencies
from dsp_tools.cli.utils import get_creds
from dsp_tools.commands.create.lists_only import create_lists_only
from dsp_tools.commands.excel2json.old_lists import validate_lists_section_with_schema
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.project.get.get import get_project
from dsp_tools.commands.resume_xmlupload.resume_xmlupload import resume_xmlupload
from dsp_tools.commands.start_stack import StackConfiguration
from dsp_tools.commands.start_stack import StackHandler
from dsp_tools.commands.validate_data.validate_data import validate_data
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file


def call_start_stack(args: argparse.Namespace) -> bool:
    check_docker_health()
    stack_handler = StackHandler(
        StackConfiguration(
            max_file_size=args.max_file_size,
            enforce_docker_system_prune=args.prune,
            suppress_docker_system_prune=args.no_prune,
            latest_dev_version=args.latest,
            upload_test_data=args.with_test_data,
            custom_host=args.custom_host,
        )
    )
    return stack_handler.start_stack()


def call_stop_stack() -> bool:
    check_docker_health()
    stack_handler = StackHandler(StackConfiguration())
    return stack_handler.stop_stack()


def call_upload_files(args: argparse.Namespace) -> bool:
    xml_path = Path(args.xml_file)
    image_dir = Path(args.imgdir)
    network_requirements = NetworkRequirements(api_url=args.server)
    path_requirements = PathDependencies([xml_path], required_directories=[image_dir])
    check_input_dependencies(path_requirements, network_requirements)

    return upload_files(
        xml_file=xml_path,
        creds=get_creds(args),
        imgdir=image_dir,
    )


def call_ingest_files(args: argparse.Namespace) -> bool:
    check_input_dependencies(network_dependencies=NetworkRequirements(api_url=args.server))
    return ingest_files(creds=get_creds(args), shortcode=args.shortcode)


def call_ingest_xmlupload(args: argparse.Namespace) -> bool:
    xml_path = Path(args.xml_file)
    required_files = [xml_path]
    id2iri_file = args.id2iri_file
    if id2iri_file:
        required_files.append(Path(id2iri_file))
    network_requirements = NetworkRequirements(args.server, always_requires_docker=True)
    path_deps = PathDependencies(required_files)
    check_input_dependencies(path_deps, network_requirements)

    interrupt_after = args.interrupt_after if args.interrupt_after > 0 else None
    return ingest_xmlupload(
        xml_file=xml_path,
        creds=get_creds(args),
        interrupt_after=interrupt_after,
        skip_validation=args.skip_validation,
        skip_ontology_validation=args.skip_ontology_validation,
        id2iri_file=id2iri_file,
        do_not_request_resource_metadata_from_db=args.do_not_request_resource_metadata_from_db,
    )


def call_xmlupload(args: argparse.Namespace) -> bool:
    xml_path = Path(args.xmlfile)
    required_files = [xml_path]
    id2iri_file = args.id2iri_file
    if id2iri_file:
        required_files.append(Path(id2iri_file))
    network_requirements = NetworkRequirements(args.server, always_requires_docker=True)
    path_deps = PathDependencies(required_files, [Path(args.imgdir)])
    check_input_dependencies(path_deps, network_requirements)

    if args.validate_only:
        if parse_and_validate_xml_file(xml_path):
            print("The XML file is syntactically correct.")
            return True
        else:
            return False  # detailed error report has already been printed
    else:
        interrupt_after = args.interrupt_after if args.interrupt_after > 0 else None
        match args.validation_severity:
            case "info":
                severity = ValidationSeverity.INFO
            case "warning":
                severity = ValidationSeverity.WARNING
            case "error":
                severity = ValidationSeverity.ERROR
            case _:
                raise InputError(
                    f"The entered validation severity '{args.validation_severity}' "
                    f"is not part of the allowed values: info, warning, error."
                )
        return xmlupload(
            input_file=xml_path,
            creds=get_creds(args),
            imgdir=args.imgdir,
            config=UploadConfig(
                interrupt_after=interrupt_after,
                skip_iiif_validation=args.no_iiif_uri_validation,
                skip_validation=args.skip_validation,
                ignore_duplicate_files_warning=args.ignore_duplicate_files_warning,
                validation_severity=severity,
                skip_ontology_validation=args.skip_ontology_validation,
                do_not_request_resource_metadata_from_db=args.do_not_request_resource_metadata_from_db,
                id2iri_file=id2iri_file,
            ),
        )


def call_validate_data(args: argparse.Namespace) -> bool:
    xml_path = Path(args.xmlfile)
    required_files = [xml_path]
    id2iri_file = args.id2iri_file
    if id2iri_file:
        required_files.append(Path(id2iri_file))
    network_requirements = NetworkRequirements(args.server, always_requires_docker=True)
    path_deps = PathDependencies(required_files)
    check_input_dependencies(path_deps, network_requirements)

    return validate_data(
        filepath=xml_path,
        creds=get_creds(args),
        save_graphs=args.save_graphs,
        ignore_duplicate_files_warning=args.ignore_duplicate_files_warning,
        skip_ontology_validation=args.skip_ontology_validation,
        id2iri_file=id2iri_file,
        do_not_request_resource_metadata_from_db=args.do_not_request_resource_metadata_from_db,
    )


def call_resume_xmlupload(args: argparse.Namespace) -> bool:
    # this does not need docker if not on localhost, as does not need to validate
    check_input_dependencies(network_dependencies=NetworkRequirements(args.server))
    return resume_xmlupload(
        creds=get_creds(args),
        skip_first_resource=args.skip_first_resource,
    )


def call_get(args: argparse.Namespace) -> bool:
    network_dependencies = NetworkRequirements(args.server)
    path_dependencies = PathDependencies(required_directories=[Path(args.project_definition).parent])
    check_input_dependencies(path_dependencies, network_dependencies)

    return get_project(
        project_identifier=args.project,
        outfile_path=args.project_definition,
        creds=get_creds(args),
        verbose=args.verbose,
    )


def call_create(args: argparse.Namespace) -> bool:
    network_dependencies = NetworkRequirements(args.server)
    path_dependencies = PathDependencies([Path(args.project_definition)])
    check_input_dependencies(path_dependencies, network_dependencies)

    success = False
    match args.lists_only, args.validate_only:
        case True, True:
            success = validate_lists_section_with_schema(args.project_definition)
            print("'Lists' section of the JSON project file is syntactically correct and passed validation.")
        case True, False:
            success = create_lists_only(
                project_file_as_path_or_parsed=args.project_definition,
                creds=get_creds(args),
            )
        case False, True:
            success = validate_project(args.project_definition)
            print("JSON project file is syntactically correct and passed validation.")
        case False, False:
            success = create_project(
                project_file_as_path_or_parsed=args.project_definition,
                creds=get_creds(args),
                verbose=args.verbose,
            )
    return success
