from flask_restful import Resource
from werkzeug import Response
from flask import make_response


class Health(Resource):

    def get(self) -> Response:
        return make_response({'status': 'ok', 'ml-brand-gender': 'healthy'}, 200)
