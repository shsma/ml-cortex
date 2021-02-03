from app.errors import BaseHttpError, ApplicationException


def add_error_handler(app) -> None:
    @app.errorhandler(BaseHttpError)
    def handle_http_error(e: BaseHttpError):
        return {
            'error': {
                'type': type(e).__name__,
                'description': str(e)
            }
        }, e.status

    @app.errorhandler(ApplicationException)
    def handle_base_error(e: ApplicationException):
        return {
            'error': {
                'type': type(e).__name__,
                'description': str(e)
            }
        }, 503

    @app.errorhandler(Exception)
    def handle_error(e: Exception):
        return {
            'error': {
                'type': type(e).__name__,
                'description': str(e)
            }
        }, 500
