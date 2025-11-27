import argparse
from pathlib import Path

from dsp_tools.cli.args import PathDependencies
from dsp_tools.cli.utils import check_path_dependencies
from dsp_tools.commands.excel2json.lists.make_lists import excel2lists
from dsp_tools.commands.excel2json.old_lists import old_excel2lists
from dsp_tools.commands.excel2json.project import excel2json
from dsp_tools.commands.excel2json.project import old_excel2json
from dsp_tools.commands.excel2json.properties import excel2properties
from dsp_tools.commands.excel2json.resources import excel2resources
from dsp_tools.commands.id2iri import id2iri
from dsp_tools.commands.update_legal.core import update_legal_metadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties


def call_id2iri(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies([Path(args.xmlfile), Path(args.mapping)]))
    return id2iri(
        xml_file=args.xmlfile,
        json_file=args.mapping,
        remove_resource_if_id_in_mapping=args.remove_resources,
    )


def call_excel2properties(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies([Path(args.excelfile)]))
    _, _, success = excel2properties(
        excelfile=args.excelfile,
        path_to_output_file=args.properties_section,
    )
    return success


def call_excel2resources(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies([Path(args.excelfile)]))
    _, _, success = excel2resources(
        excelfile=args.excelfile,
        path_to_output_file=args.resources_section,
    )
    return success


def call_old_excel2lists(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies(required_directories=[Path(args.excelfolder)]))
    _, success = old_excel2lists(
        excelfolder=args.excelfolder,
        path_to_output_file=args.lists_section,
        verbose=args.verbose,
    )
    return success


def call_excel2lists(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies(required_directories=[Path(args.excelfolder)]))
    _, success = excel2lists(
        excelfolder=args.excelfolder,
        path_to_output_file=args.lists_section,
    )
    return success


def call_excel2json(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies(required_directories=[Path(args.excelfolder)]))
    return excel2json(
        data_model_files=args.excelfolder,
        path_to_output_file=args.project_definition,
    )


def call_old_excel2json(args: argparse.Namespace) -> bool:
    check_path_dependencies(PathDependencies(required_directories=[Path(args.excelfolder)]))
    return old_excel2json(
        data_model_files=args.excelfolder,
        path_to_output_file=args.project_definition,
    )


def call_update_legal(args: argparse.Namespace) -> bool:
    required_files = [Path(args.xmlfile)]
    if args.fixed_errors:
        required_files.append(Path(args.fixed_errors))
    check_path_dependencies(PathDependencies(required_files))
    properties = LegalProperties(
        authorship_prop=args.authorship_prop,
        copyright_prop=args.copyright_prop,
        license_prop=args.license_prop,
    )
    defaults = LegalMetadataDefaults(
        authorship_default=args.authorship_default,
        copyright_default=args.copyright_default,
        license_default=args.license_default,
    )
    return update_legal_metadata(
        input_file=Path(args.xmlfile),
        properties=properties,
        defaults=defaults,
        fixed_errors_file=Path(args.fixed_errors) if args.fixed_errors else None,
        treat_invalid_licenses_as_unknown=args.treat_invalid_licenses_as_unknown,
    )
