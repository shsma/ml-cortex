from functools import wraps
from ssense_logger.app_logger import AppLogger
from app.config import Config

app_logger = AppLogger(app_name=Config.APP_NAME, env=Config.ENV)


def exception_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except BaseException as e:
            app_logger.error(msg=f'{func.__name__} failed: {e.__str__()}')

    return wrapper
