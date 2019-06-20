import argparse
import sys

from knora import Knora


def program(args):
    # parse the arguments of the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", default="test", help="The password for login")

    args = parser.parse_args(args)

    # create the knora connection object
    con = Knora(args.server)
    con.login(args.user, args.password)
    con.reset_triplestore_content()


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
