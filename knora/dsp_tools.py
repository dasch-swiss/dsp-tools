"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import datetime
import os
import sys

import pkg_resources  # part of setuptools

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dsplib.utils.onto_create_lists import create_lists
from dsplib.utils.onto_create_ontology import create_ontology
from dsplib.utils.onto_get import get_ontology
from dsplib.utils.excel_to_json_lists import list_excel2json, validate_list_with_schema
from dsplib.utils.onto_validate import validate_ontology
from dsplib.utils.xml_upload import xml_upload


def program(args: list) -> None:
    """
    The program parses the command line arguments and calls the requested action

    Args:
        args: list of arguments passed by the user from the command line

    Returns:
        None
    """
    version = pkg_resources.require('dsp-tools')[0].version
    now = datetime.datetime.now()

    # parse the arguments of the command line
    parser = argparse.ArgumentParser(
            description=f'dsp-tools (Version {version}) DaSCH Service Platform data modelling tools (© {now.year} by DaSCH).')

    subparsers = parser.add_subparsers(title='Subcommands', description='Valid subcommands are', help='sub-command help')

    parser_create = subparsers.add_parser('create', help='Upload an ontology and/or list(s) from a JSON file to the DaSCH '
                                                         'Service Platform')
    parser_create.set_defaults(action='create')
    parser_create.add_argument('-s', '--server', type=str, default='http://0.0.0.0:3333', help='URL of the DSP server')
    parser_create.add_argument('-u', '--user', default='root@example.com', help='Username for DSP server')
    parser_create.add_argument('-p', '--password', default='test', help='The password for login')
    parser_create.add_argument('-V', '--validate', action='store_true', help='Do only validation of JSON, no upload of the '
                                                                             'ontology')
    parser_create.add_argument('-L', '--listfile', type=str, default='lists.json', help='Name of list node informationfile')
    parser_create.add_argument('-l', '--lists', action='store_true', help='Upload only the list(s)')
    parser_create.add_argument('-v', '--verbose', action='store_true', help='Verbose feedback')
    parser_create.add_argument('-d', '--dump', action='store_true', help='dump test files for DSP-API requests')
    parser_create.add_argument('datamodelfile', help='path to data model file')

    parser_get = subparsers.add_parser('get', help='Get the ontology (data model) of a project from the DaSCH Service Platform.')
    parser_get.set_defaults(action='get')
    parser_get.add_argument('-u', '--user', default='root@example.com', help='Username for DSP server')
    parser_get.add_argument('-p', '--password', default='test', help='The password for login')
    parser_get.add_argument('-s', '--server', type=str, default='http://0.0.0.0:3333', help='URL of the DSP server')
    parser_get.add_argument('-P', '--project', type=str, help='Shortcode, shortname or iri of project', required=True)
    parser_get.add_argument('-v', '--verbose', action='store_true', help='Verbose feedback')
    parser_get.add_argument('datamodelfile', help='Path to the file the ontology should be written to', default='onto.json')

    parser_upload = subparsers.add_parser('xmlupload', help='Upload data from an XML file to the DaSCH Service Platform.')
    parser_upload.set_defaults(action='xmlupload')
    parser_upload.add_argument('-s', '--server', type=str, default='http://0.0.0.0:3333', help='URL of the DSP server')
    parser_upload.add_argument('-u', '--user', type=str, default='root@example.com', help='Username for DSP server')
    parser_upload.add_argument('-p', '--password', type=str, default='test', help='The password for login')
    parser_upload.add_argument('-V', '--validate', action='store_true', help='Do only validation of XML, no upload of the data')
    parser_upload.add_argument('-i', '--imgdir', type=str, default='.', help='Path to folder containing the images')
    parser_upload.add_argument('-S', '--sipi', type=str, default='http://0.0.0.0:1024', help='URL of SIPI server')
    parser_upload.add_argument('-v', '--verbose', action='store_true', help='Verbose feedback')
    parser_upload.add_argument('xmlfile', help='path to xml file containing the data', default='data.xml')

    parser_excel_lists = subparsers.add_parser('excel', help='Create a JSON list from one or multiple Excel files. The JSON '
                                                             'list can be integrated into a JSON ontology. If the list should '
                                                             'contain multiple languages, an Excel file has to be used for '
                                                             'each language. The filenames should contain the language as '
                                                             'label, p.ex. liste_de.xlsx, list_en.xlsx. The language is then '
                                                             'taken from the filename. Only files with extension .xlsx are '
                                                             'considered.')
    parser_excel_lists.set_defaults(action='excel')
    parser_excel_lists.add_argument('-l', '--listname', type=str, help='Name of the list to be created (filename is taken if '
                                                                       'omitted)', default=None)
    parser_excel_lists.add_argument('excelfolder', help='Path to the folder containing the Excel file(s)', default='lists')
    parser_excel_lists.add_argument('outfile', help='Path to the output JSON file containing the list data', default='list.json')

    args = parser.parse_args(args)

    if not hasattr(args, 'action'):
        parser.print_help(sys.stderr)
        exit(0)

    if args.action == 'create':
        if args.lists:
            if args.validate:
                validate_list_with_schema(args.datamodelfile)
            else:
                create_lists(input_file=args.datamodelfile,
                             lists_file=args.listfile,
                             server=args.server,
                             user=args.user,
                             password=args.password,
                             verbose=args.verbose,
                             dump=args.dump)
        else:
            if args.validate:
                validate_ontology(args.datamodelfile)
            else:
                create_ontology(input_file=args.datamodelfile,
                                lists_file=args.listfile,
                                server=args.server,
                                user=args.user,
                                password=args.password,
                                verbose=args.verbose,
                                dump=args.dump if args.dump else False)
    elif args.action == 'get':
        get_ontology(projident=args.project,
                     outfile=args.datamodelfile,
                     server=args.server,
                     user=args.user,
                     password=args.password,
                     verbose=args.verbose)
    elif args.action == 'xmlupload':
        xml_upload(input_file=args.xmlfile,
                   server=args.server,
                   user=args.user,
                   password=args.password,
                   imgdir=args.imgdir,
                   sipi=args.sipi,
                   verbose=args.verbose,
                   validate_only=args.validate)
    elif args.action == 'excel':
        list_excel2json(listname=args.listname,
                        excelfolder=args.excelfolder,
                        outfile=args.outfile)


def main():
    """Main entry point of the program as referenced in setup.py"""
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
