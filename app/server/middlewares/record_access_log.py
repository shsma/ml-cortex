import math
import time

from flask import current_app as app, request, g
from ddtrace.helpers import get_correlation_ids
from ssense_logger.access_logger import AccessLogger
from werkzeug import Response

from app.server.middlewares.record_request_id import REQUEST_ID


def record_access_log(resp: Response) -> Response:
    """
    Executed after a request.
    Note: we need to have the full function signature, even if some arguments are not used
    """
    _res_size = 0
    if resp is not None and resp.data is not None:
        _res_size = len(resp.data)

    access_logger = AccessLogger(app_name=app.config['APP_NAME'], env=app.config['ENV'], get_correlation_ids=get_correlation_ids)
    access_logger.log_access(req_id=getattr(g, 'request_id', f'{REQUEST_ID} not set'),
                             ip=request.headers.get('x-forwarded-for', 'x-forwarded-for not set'),
                             method=request.method,
                             route=request.path,
                             user_agent=request.user_agent.to_header(),
                             res_code=resp.status_code,
                             res_size=_res_size,
                             res_time=math.ceil((time.time() - float(getattr(g, 'time_of_request', 0))) * 1000),
                             http_version='HTTP/1.1')
    return resp
