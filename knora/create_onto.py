import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dsplib.utils.onto_validate import validate_list, validate_ontology
from dsplib.utils.onto_create_lists import create_lists
from dsplib.utils.onto_create_ontology import create_ontology
from dsplib.utils.onto_get import get_ontology


def program(args):
    #
    # parse the arguments of the command line
    #
    parser = argparse.ArgumentParser(
        description="A program to create and manipulate ontologies based on the DaSCH Service Platform and Knora"
    )
    subparsers = parser.add_subparsers(title="Subcommands",
                                       description='Valid subcommands are',
                                       help='sub-command help')


    parser_create = subparsers.add_parser('create', help='Create ontologies, lists etc.')
    parser_create.set_defaults(action="create")
    parser_create.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser_create.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
    parser_create.add_argument("-p", "--password", default="test", help="The password for login")
    parser_create.add_argument("-V", "--validate", action='store_true', help="Do only validation of JSON, no upload of the ontology")
    parser_create.add_argument("datamodelfile", help="path to data model file")
    parser_create.add_argument("-L", "--listfile", type=str, default="lists.json", help="Name of list node informationfile")
    parser_create.add_argument("-l", "--lists", action='store_true', help="Only create the lists")
    parser_create.add_argument("-v", "--verbose", action="store_true", help="Verbose feedback")

    parser_get = subparsers.add_parser('get', help='Get project/ontology information from server')
    parser_get.set_defaults(action="get")
    parser_get.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
    parser_get.add_argument("-p", "--password", default="test", help="The password for login")
    parser_get.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser_get.add_argument("-P", "--project", type=str, help="Shortcode, shortname or iri of project", required=True)
    parser_get.add_argument("outfile", help="path to data model file", default="onto.json")
    parser_get.add_argument("-v", "--verbose", action="store_true", help="Verbose feedback")

    args = parser.parse_args(args)

    if args.action == "create":
        if args.lists:
            if args.validate:
                validate_list(args.datamodelfile)
            else:
                create_lists(args.datamodelfile, args.listfile)
        else:
            if args.validate:
                validate_ontology(args.datamodelfile)
            else:
                create_ontology(args.datamodelfile, args.listfile, args.server, args.user, args.password, args.verbose)
    elif args.action == "get":
        get_ontology(args.project, args.outfile, args.server, args.user, args.password, args.verbose)


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])

