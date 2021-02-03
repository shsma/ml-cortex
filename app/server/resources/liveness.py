from flask import make_response
from flask_restful import Resource
from werkzeug import Response


class Liveness(Resource):

    @staticmethod
    def get() -> Response:
        return make_response({'status': 'ok', 'ml-brand-gender': 'alive'})
