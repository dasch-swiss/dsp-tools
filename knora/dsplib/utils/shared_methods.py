import re
import time
from datetime import datetime
from typing import Union, Callable, Any, Optional

from lxml import etree
from requests import RequestException

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.helpers import BaseError


def login(server: str, user: str, password: str) -> Connection:
    """
    Logs in and returns the active connection. Raises a BaseError if the login fails.

    Args:
        server: URL of the DSP server to connect to
        user: Username (e-mail)
        password: Password of the user

    Return:
        Connection instance
    """
    con = Connection(server)
    try_network_action(
        action=lambda: con.login(email=user, password=password),
        failure_msg="ERROR: Cannot login to DSP server"
    )
    return con


def try_network_action(
    failure_msg: str,
    action: Callable[..., Any]
) -> Any:
    """
    Helper method that tries 7 times to execute an action. Each time, it catches ConnectionError and
    requests.exceptions.RequestException, which lead to a waiting time and a retry. The waiting times are 1,
    2, 4, 8, 16, 32, 64 seconds.

    In case of a BaseError or Exception, a BaseError is raised with failure_msg, followed by the original
    error message.

    If there is no success at the end, a BaseError with failure_msg is raised.

    Args:
        failure_msg: message of the raised BaseError if action cannot be executed
        action: a lambda with the code to be executed

    Returns:
        the return value of action
    """

    for i in range(7):
        try:
            return action()
        except ConnectionError:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except RequestException:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except BaseError as err:
            if re.search(r'try again later', err.message) or re.search(r'status code=5\d\d', err.message):
                print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
                time.sleep(2 ** i)
                continue
            if hasattr(err, 'message'):
                err_message = err.message
            else:
                err_message = str(err).replace('\n', ' ')
                err_message = err_message[:150] if len(err_message) > 150 else err_message
            raise BaseError(f"{failure_msg} Error message: {err_message}")
        except Exception as exc:
            if hasattr(exc, 'message'):
                exc_message = exc.message
            else:
                exc_message = str(exc).replace('\n', ' ')
                exc_message = exc_message[:150] if len(exc_message) > 150 else exc_message
            raise BaseError(f"{failure_msg} Error message: {exc_message}")

    raise BaseError(failure_msg)


def validate_xml_against_schema(input_file: str, schema_file: str) -> bool:
    """
    Validates an XML file against an XSD schema

    Args:
        input_file: the XML file to be validated
        schema_file: the schema against which the XML file should be validated

    Returns:
        True if the XML file is valid. Otherwise, a BaseError with a detailed error log is raised
    """
    xmlschema = etree.XMLSchema(etree.parse(schema_file))
    doc = etree.parse(input_file)

    if xmlschema.validate(doc):
        print("The XML file is syntactically correct and passed validation.")
        return True
    else:
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"\n  Line {error.line}: {error.message}"
        raise BaseError(error_msg)
