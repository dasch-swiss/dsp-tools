"""
The code in this file handles the arguments passed by the user from the command line and calls the requested actions.
"""
import argparse
import datetime
import sys
from importlib.metadata import version

from knora.dsplib.utils.excel_to_json_lists import list_excel2json, validate_list_with_schema
from knora.dsplib.utils.excel_to_json_properties import properties_excel2json
from knora.dsplib.utils.excel_to_json_resources import resources_excel2json
from knora.dsplib.utils.id_to_iri import id_to_iri
from knora.dsplib.utils.onto_create_lists import create_lists
from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.onto_get import get_ontology
from knora.dsplib.utils.onto_validate import validate_project
from knora.dsplib.utils.xml_upload import xml_upload


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

    # parse the arguments of the command line
    parser = argparse.ArgumentParser(
        description=f'dsp-tools (Version {dsp_tools_version}) DaSCH Service Platform data modelling tools (© {now.year} by DaSCH).')

    subparsers = parser.add_subparsers(title='Subcommands', description='Valid subcommands are',
                                       help='sub-command help')

    parser_create = subparsers.add_parser('create',
                                          help='Upload an ontology and/or list(s) from a JSON file to the DaSCH '
                                               'Service Platform')
    parser_create.set_defaults(action='create')
    parser_create.add_argument('-s', '--server', type=str, default=default_localhost, help=url_text)
    parser_create.add_argument('-u', '--user', default=default_user, help=username_text)
    parser_create.add_argument('-p', '--password', default=default_pw, help=password_text)
    parser_create.add_argument('-V', '--validate-only', action='store_true',
                               help='Do only validation of JSON, no upload of the '
                                    'ontology')
    parser_create.add_argument('-l', '--lists-only', action='store_true', help='Upload only the list(s)')
    parser_create.add_argument('-v', '--verbose', action='store_true', help=verbose_text)
    parser_create.add_argument('-d', '--dump', action='store_true', help='dump test files for DSP-API requests')
    parser_create.add_argument('datamodelfile', help='path to data model file')

    parser_get = subparsers.add_parser('get',
                                       help='Get the ontology (data model) of a project from the DaSCH Service Platform.')
    parser_get.set_defaults(action='get')
    parser_get.add_argument('-u', '--user', default=default_user, help=username_text)
    parser_get.add_argument('-p', '--password', default=default_pw, help=password_text)
    parser_get.add_argument('-s', '--server', type=str, default=default_localhost, help=url_text)
    parser_get.add_argument('-P', '--project', type=str, help='Shortcode, shortname or iri of project', required=True)
    parser_get.add_argument('-v', '--verbose', action='store_true', help=verbose_text)
    parser_get.add_argument('datamodelfile', help='Path to the file the ontology should be written to',
                            default='onto.json')

    parser_upload = subparsers.add_parser('xmlupload',
                                          help='Upload data from an XML file to the DaSCH Service Platform.')
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
    parser_upload.add_argument('xmlfile', help='path to xml file containing the data', default='data.xml')

    parser_excel_lists = subparsers.add_parser('excel',
                                               help='Create a JSON list from one or multiple Excel files. The JSON '
                                                    'list can be integrated into a JSON ontology. If the list should '
                                                    'contain multiple languages, an Excel file has to be used for '
                                                    'each language. The filenames should contain the language as '
                                                    'label, p.ex. liste_de.xlsx, list_en.xlsx. The language is then '
                                                    'taken from the filename. Only files with extension .xlsx are '
                                                    'considered.')
    parser_excel_lists.set_defaults(action='excel')
    parser_excel_lists.add_argument('-l', '--listname', type=str,
                                    help='Name of the list to be created (filename is taken if '
                                         'omitted)', default=None)
    parser_excel_lists.add_argument('excelfolder', help='Path to the folder containing the Excel file(s)',
                                    default='lists')
    parser_excel_lists.add_argument('outfile', help='Path to the output JSON file containing the list data',
                                    default='list.json')

    parser_excel_resources = subparsers.add_parser('excel2resources',
                                                   help='Create a JSON file from an Excel file containing '
                                                        'resources for a DSP ontology. ')
    parser_excel_resources.set_defaults(action='excel2resources')
    parser_excel_resources.add_argument('excelfile', help='Path to the Excel file containing the resources',
                                        default='resources.xlsx')
    parser_excel_resources.add_argument('outfile', help='Path to the output JSON file containing the resource data',
                                        default='resources.json')

    parser_excel_properties = subparsers.add_parser('excel2properties',
                                                    help='Create a JSON file from an Excel file containing '
                                                         'properties for a DSP ontology. ')
    parser_excel_properties.set_defaults(action='excel2properties')
    parser_excel_properties.add_argument('excelfile', help='Path to the Excel file containing the properties',
                                         default='properties.xlsx')
    parser_excel_properties.add_argument('outfile', help='Path to the output JSON file containing the properties data',
                                         default='properties.json')

    parser_id2iri = subparsers.add_parser('id2iri',
                                          help='Replace internal IDs in an XML with their corresponding IRIs from a provided JSON file.')
    parser_id2iri.set_defaults(action='id2iri')
    parser_id2iri.add_argument('xmlfile', help='Path to the XML file containing the data to be replaced')
    parser_id2iri.add_argument('jsonfile',
                               help='Path to the JSON file containing the mapping of internal IDs and their respective IRIs')
    parser_id2iri.add_argument('--outfile', default=None,
                               help='Path to the XML output file containing the replaced IDs (optional)')
    parser_id2iri.add_argument('-v', '--verbose', action='store_true', help=verbose_text)

    args = parser.parse_args(user_args)

    if not hasattr(args, 'action'):
        parser.print_help(sys.stderr)
        exit(0)

    if args.action == 'create':
        if args.lists_only:
            if args.validate_only:
                validate_list_with_schema(args.datamodelfile)
            else:
                create_lists(input_file=args.datamodelfile,
                             server=args.server,
                             user=args.user,
                             password=args.password,
                             dump=args.dump)
        else:
            if args.validate_only:
                if validate_project(args.datamodelfile):
                    print('Data model is syntactically correct and passed validation.')
                    exit(0)
            else:
                create_project(input_file=args.datamodelfile,
                               server=args.server,
                               user_mail=args.user,
                               password=args.password,
                               verbose=args.verbose,
                               dump=args.dump if args.dump else False)
    elif args.action == 'get':
        get_ontology(project_identifier=args.project,
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
                   validate_only=args.validate,
                   incremental=args.incremental)
    elif args.action == 'excel':
        list_excel2json(listname=args.listname,
                        excelfolder=args.excelfolder,
                        outfile=args.outfile)
    elif args.action == 'excel2resources':
        resources_excel2json(excelfile=args.excelfile,
                             outfile=args.outfile)
    elif args.action == 'excel2properties':
        properties_excel2json(excelfile=args.excelfile,
                              outfile=args.outfile)
    elif args.action == 'id2iri':
        id_to_iri(xml_file=args.xmlfile,
                  json_file=args.jsonfile,
                  out_file=args.outfile,
                  verbose=args.verbose)


def main() -> None:
    """Main entry point of the program as referenced in setup.py"""
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
