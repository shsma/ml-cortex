import flask_injector
import injector
from ddtrace.helpers import get_correlation_ids
from ssense_logger.app_logger import AppLogger


class AppLoggerModule(injector.Module):
    def __init__(self, app: str, env: str):
        self.app = app
        self.env = env

    def configure(self, binder):
        binder.bind(AppLogger,
                    to=self.create,
                    scope=flask_injector.singleton)

    @injector.inject
    def create(self) -> AppLogger:
        return AppLogger(app_name=self.app, env=self.env, get_correlation_ids=get_correlation_ids)
