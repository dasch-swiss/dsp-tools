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
