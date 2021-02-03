import uuid
from typing import NoReturn

from flask import request, g

REQUEST_ID = 'x-request-id'


def record_request_id() -> NoReturn:
    """
    Adds the incoming request id to the application context,
    or generates a random uuid if one wasn't provided.
    """
    g.request_id = request.headers.get(REQUEST_ID, str(uuid.uuid4()))
