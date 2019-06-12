import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from knora import KnoraError, Knora
import sys


def main(args):
    # parse the arguments of the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")

    args = parser.parse_args(args)

    # create the knora connection object
    con = Knora(args.server)
    con.login(args.user, args.password)
    con.reset_triplestore_content()

if __name__ == '__main__':
    main(sys.argv[1:])
