import re
import time
from datetime import datetime
from typing import Union, Callable, Any, Optional

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
        object=con,
        method="login",
        kwargs={"email": user, "password": password},
        error_message_on_failure="ERROR: Cannot login to DSP server"
    )
    return con


def try_network_action(
    error_message_on_failure: str,
    method: Union[str, Callable[..., Any]],
    object: Optional[Any] = None,
    kwargs: Optional[dict[str, Any]] = None
) -> Any:
    """
    Helper method that tries 7 times to execute an action. Each time, it catches ConnectionError and
    requests.exceptions.RequestException, which lead to a waiting time and a retry. The waiting times are 1,
    2, 4, 8, 16, 32, 64 seconds.

    In case of a BaseError or Exception, a BaseError is raised with error_message_on_failure, followed by the original
    error message.

    If there is no success at the end, a BaseError with error_message_on_failure is raised.

    Args:
        error_message_on_failure: message of the raised BaseError if action cannot be executed
        method: either a callable to be called on its own, or a method name (as string) to be called on object
        object: if provided, it must be a python variable/object, accompanied by a method name (as string)
        kwargs: if provided, a dict with the arguments passed to method

    Returns:
        the return value of action
    """

    for i in range(7):
        try:
            if object and isinstance(method, str):
                if not kwargs:
                    return getattr(object, method)()
                else:
                    return getattr(object, method)(**kwargs)
            else:
                if not kwargs:
                    return method()
                else:
                    return method(**kwargs)
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
            raise BaseError(f"{error_message_on_failure} Error message: {err_message}")
        except Exception as exc:
            if hasattr(exc, 'message'):
                exc_message = exc.message
            else:
                exc_message = str(exc).replace('\n', ' ')
                exc_message = exc_message[:150] if len(exc_message) > 150 else exc_message
            raise BaseError(f"{error_message_on_failure} Error message: {exc_message}")

    raise BaseError(error_message_on_failure)
