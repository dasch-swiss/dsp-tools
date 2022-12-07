"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import datetime
import os
import sys
from importlib.metadata import version

from knora.dsplib.utils.excel_to_json_lists import excel2lists, validate_lists_section_with_schema
from knora.dsplib.utils.excel_to_json_project import excel2json
from knora.dsplib.utils.excel_to_json_properties import excel2properties
from knora.dsplib.utils.excel_to_json_resources import excel2resources
from knora.dsplib.utils.id_to_iri import id_to_iri
from knora.dsplib.utils.onto_create_lists import create_lists
from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.onto_get import get_ontology
from knora.dsplib.utils.onto_validate import validate_project
from knora.dsplib.utils.shared import validate_xml_against_schema
from knora.dsplib.utils.stack_handling import start_stack, stop_stack
from knora.dsplib.utils.xml_upload import xml_upload
from knora.excel2xml import excel2xml


def program(user_args: list[str]) -> None:
    """
    The program parses the command line arguments and calls the requested action

    Args:
        user_args: list of arguments passed by the user from the command line

    Returns:
        None
    """
    # help texts
    username_text = 'Username (e-mail) for DSP server'
    password_text = 'The password for login'
    url_text = 'URL of the DSP server'
    verbose_text = 'Verbose feedback'

    # default values
    default_localhost = 'http://0.0.0.0:3333'
    default_user = 'root@example.com'
    default_pw = 'test'
    dsp_tools_version = version('dsp-tools')
    now = datetime.datetime.now()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # parse the arguments of the command line
    parser = argparse.ArgumentParser(description=f'dsp-tools (Version {dsp_tools_version}) DaSCH Service Platform data '
                                                 f'modelling tools (© {now.year} by DaSCH).')
    subparsers = parser.add_subparsers(title='Subcommands', description='Valid subcommands are', help='sub-command help')

    # create
    parser_create = subparsers.add_parser('create', help='Upload a project and/or list(s) from a JSON project file to '
                                               'the DaSCH Service Platform')
    parser_create.set_defaults(action='create')
    parser_create.add_argument('-s', '--server', type=str, default=default_localhost, help=url_text)
    parser_create.add_argument('-u', '--user', default=default_user, help=username_text)
    parser_create.add_argument('-p', '--password', default=default_pw, help=password_text)
    parser_create.add_argument('-V', '--validate-only', action='store_true', help='Only validate the project against '
                               'the JSON schema, without uploading it')
    parser_create.add_argument('-l', '--lists-only', action='store_true', help='Upload only the list(s)')
    parser_create.add_argument('-v', '--verbose', action='store_true', help=verbose_text)
    parser_create.add_argument('-d', '--dump', action='store_true', help='dump test files for DSP-API requests')
    parser_create.add_argument('projectfile', help='path to a JSON project file')

    # get
    parser_get = subparsers.add_parser('get', help='Get a project from the DaSCH Service Platform.')
    parser_get.set_defaults(action='get')
    parser_get.add_argument('-u', '--user', default=default_user, help=username_text)
    parser_get.add_argument('-p', '--password', default=default_pw, help=password_text)
    parser_get.add_argument('-s', '--server', type=str, default=default_localhost, help=url_text)
    parser_get.add_argument('-P', '--project', type=str, help='Shortcode, shortname or iri of project', required=True)
    parser_get.add_argument('-v', '--verbose', action='store_true', help=verbose_text)
    parser_get.add_argument('projectfile', help='Path to the file the project should be written to',
                            default='project.json')

    # xmlupload
    parser_upload = subparsers.add_parser('xmlupload', help='Upload data from an XML file to the DaSCH Service Platform.')
    parser_upload.set_defaults(action='xmlupload')
    parser_upload.add_argument('-s', '--server', type=str, default=default_localhost, help=url_text)
    parser_upload.add_argument('-u', '--user', type=str, default=default_user, help=username_text)
    parser_upload.add_argument('-p', '--password', type=str, default=default_pw, help=password_text)
    parser_upload.add_argument('-V', '--validate', action='store_true',
                               help='Do only validation of XML, no upload of the data')
    parser_upload.add_argument('-i', '--imgdir', type=str, default='.', help='Path to folder containing the images')
    parser_upload.add_argument('-S', '--sipi', type=str, default='http://0.0.0.0:1024', help='URL of SIPI server')
    parser_upload.add_argument('-v', '--verbose', action='store_true', help=verbose_text)
    parser_upload.add_argument('-I', '--incremental', action='store_true', help='Incremental XML upload')
    parser_upload.add_argument('-m', '--metrics', action='store_true', help='Write metrics into a "metrics" folder in '
                                                                            'the current working directory')
    parser_upload.add_argument('xmlfile', help='path to xml file containing the data', default='data.xml')

    # excel2json
    parser_excel2json = subparsers.add_parser(
        'excel2json',
        help='Create a JSON project file from a folder containing the required Excel files (lists folder, '
             'properties.xlsx, resources.xlsx)'
    )
    parser_excel2json.set_defaults(action='excel2json')
    parser_excel2json.add_argument('data_model_files', help='Path to the folder containing the Excel files')
    parser_excel2json.add_argument('outfile', help='Path to the output JSON file')

    # excel2lists
    parser_excel_lists = subparsers.add_parser(
        'excel2lists',
        help='Create the "lists" section of a JSON project file from one or multiple Excel files. If the list should '
             'contain multiple languages, a separate file has to be used for each language. The file names must '
             'consist of the language label, e.g. "de.xlsx", "en.xlsx". Only files with extension .xlsx are considered.'
    )
    parser_excel_lists.set_defaults(action='excel2lists')
    parser_excel_lists.add_argument('excelfolder', help='Path to the folder containing the Excel file(s)')
    parser_excel_lists.add_argument('outfile', help='Path to the output JSON file containing the "lists" section')
    parser_excel_lists.add_argument('-v', '--verbose', action='store_true', help=verbose_text)

    # excel2resources
    parser_excel_resources = subparsers.add_parser('excel2resources', help='Create a JSON file from an Excel file '
                                                   'containing resources for a DSP ontology. ')
    parser_excel_resources.set_defaults(action='excel2resources')
    parser_excel_resources.add_argument('excelfile', help='Path to the Excel file containing the resources')
    parser_excel_resources.add_argument('outfile', help='Path to the output JSON file containing the resource data')

    # excel2properties
    parser_excel_properties = subparsers.add_parser('excel2properties', help='Create a JSON file from an Excel file '
                                                    'containing properties for a DSP ontology. ')
    parser_excel_properties.set_defaults(action='excel2properties')
    parser_excel_properties.add_argument('excelfile', help='Path to the Excel file containing the properties')
    parser_excel_properties.add_argument('outfile', help='Path to the output JSON file containing the properties data')

    # id2iri
    parser_id2iri = subparsers.add_parser('id2iri', help='Replace internal IDs in an XML with their corresponding IRIs '
                                                         'from a provided JSON file.')
    parser_id2iri.set_defaults(action='id2iri')
    parser_id2iri.add_argument('xmlfile', help='Path to the XML file containing the data to be replaced')
    parser_id2iri.add_argument('jsonfile',
                               help='Path to the JSON file containing the mapping of internal IDs and their respective IRIs')
    parser_id2iri.add_argument('--outfile', default=None,
                               help='Path to the XML output file containing the replaced IDs (optional)')
    parser_id2iri.add_argument('-v', '--verbose', action='store_true', help=verbose_text)

    # excel2xml
    parser_excel2xml = subparsers.add_parser('excel2xml', help='Transform a tabular data source in CSV/XLS(X) format '
                                                               'to DSP-conforming XML. ')
    parser_excel2xml.set_defaults(action='excel2xml')
    parser_excel2xml.add_argument('datafile', help='Path to the CSV or XLS(X) file containing the data')
    parser_excel2xml.add_argument('shortcode', help='Shortcode of the project that this data belongs to')
    parser_excel2xml.add_argument('default_ontology', help='Name of the ontology that this data belongs to')

    # startup DSP stack
    parser_stackup = subparsers.add_parser('start-stack', help='Startup a local instance of the DSP stack (DSP-API and '
                                                               'DSP-APP)')
    parser_stackup.set_defaults(action='start-stack')
    parser_stackup.add_argument('--max_file_size', type=int, default=None,
                                help="max. multimedia file size allowed by SIPI, in MB (default: 250, max: 100'000)")
    parser_stackup.add_argument('--prune', action='store_true',
                                help='if set, execute "docker system prune" without asking the user')
    parser_stackup.add_argument('--no-prune', action='store_true',
                                help='if set, don\'t execute "docker system prune" (and don\'t ask)')

    # shutdown DSP-API
    parser_stackdown = subparsers.add_parser('stop-stack', help='Shut down the local instance of the DSP stack, and '
                                                                'delete all data in it')
    parser_stackdown.set_defaults(action='stop-stack')


    # call the requested action
    args = parser.parse_args(user_args)

    if not hasattr(args, 'action'):
        parser.print_help(sys.stderr)
        exit(0)

    if args.action == 'create':
        if args.lists_only:
            if args.validate_only:
                validate_lists_section_with_schema(path_to_json_project_file=args.projectfile)
                print('"Lists" section of the JSON project file is syntactically correct and passed validation.')
                exit(0)
            else:
                create_lists(input_file=args.projectfile,
                             server=args.server,
                             user=args.user,
                             password=args.password,
                             dump=args.dump)
        else:
            if args.validate_only:
                validate_project(args.projectfile)
                print('JSON project file is syntactically correct and passed validation.')
                exit(0)
            else:
                create_project(input_file=args.projectfile,
                               server=args.server,
                               user_mail=args.user,
                               password=args.password,
                               verbose=args.verbose,
                               dump=args.dump if args.dump else False)
    elif args.action == 'get':
        get_ontology(project_identifier=args.project,
                     outfile=args.projectfile,
                     server=args.server,
                     user=args.user,
                     password=args.password,
                     verbose=args.verbose)
    elif args.action == 'xmlupload':
        if args.validate:
            validate_xml_against_schema(input_file=args.xmlfile)
        else:
            xml_upload(input_file=args.xmlfile,
                       server=args.server,
                       user=args.user,
                       password=args.password,
                       imgdir=args.imgdir,
                       sipi=args.sipi,
                       verbose=args.verbose,
                       incremental=args.incremental,
                       save_metrics=args.metrics)
    elif args.action == 'excel2json':
        excel2json(data_model_files=args.data_model_files,
                      path_to_output_file=args.outfile)
    elif args.action == 'excel2lists':
        excel2lists(excelfolder=args.excelfolder,
                    path_to_output_file=args.outfile,
                    verbose=args.verbose)
    elif args.action == 'excel2resources':
        excel2resources(excelfile=args.excelfile,
                        path_to_output_file=args.outfile)
    elif args.action == 'excel2properties':
        excel2properties(excelfile=args.excelfile,
                         path_to_output_file=args.outfile)
    elif args.action == 'id2iri':
        id_to_iri(xml_file=args.xmlfile,
                  json_file=args.jsonfile,
                  out_file=args.outfile,
                  verbose=args.verbose)
    elif args.action == 'excel2xml':
        excel2xml(datafile=args.datafile,
                  shortcode=args.shortcode,
                  default_ontology=args.default_ontology)
    elif args.action == 'start-stack':
        start_stack(max_file_size=args.max_file_size,
                    enforce_docker_system_prune=args.prune,
                    suppress_docker_system_prune=args.no_prune)
    elif args.action == 'stop-stack':
        stop_stack()



def main() -> None:
    """Main entry point of the program as referenced in setup.py"""
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
