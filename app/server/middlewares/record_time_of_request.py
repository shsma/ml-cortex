import time
from typing import NoReturn

from flask import g


def record_time_of_request() -> NoReturn:
    """
    Adds the current time to the application context.
    Used later to log time it took to process a request.
    """
    g.time_of_request = time.time()
