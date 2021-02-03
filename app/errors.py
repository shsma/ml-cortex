class ApplicationException(Exception):

    def __init__(self, description):
        super().__init__(description)


class BaseHttpError(ApplicationException):
    status: int = 0


class BadRequestHttpError(BaseHttpError):
    status = 400


class NotFoundHttpError(BaseHttpError):
    status = 404


class InternalErrorHttpError(BaseHttpError):
    status = 500
