from flask import make_response
from flask_restful import Resource
from werkzeug import Response


class Home(Resource):

    def __init__(self, **kwargs):
        self.model_info = kwargs['model_info']
        self.config = kwargs['config']

    def get(self) -> Response:
        return make_response(
            {
                'app': self.config['APP_NAME'],
                'model_info': self.model_info.__dict__
            },
            200
        )
