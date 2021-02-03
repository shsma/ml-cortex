from flask import make_response, request, g
from flask_restful import Resource
from werkzeug import Response

from app.errors import BadRequestHttpError
from typing import Any


class Predict(Resource):

    def __init__(self, **kwargs):
        self.predict_service = kwargs['predict_service']
        self.app_logger = kwargs['app_logger']

    def post(self) -> Response:
        data = request.get_json()
        member_id = self._validate_member_id(data.get('data'), 'data')
        return self._predict(member_id)

    def get(self) -> Response:
        member_id = self._validate_member_id(request.args.get('memberId'))
        return self._predict(member_id)

    def _predict(self, member_id: int) -> Response:
        predictions = self.predict_service.predict(member_id, g.request_id)

        """
        Flask will no be able to serialize a list of python object instances
        So next line we map a list of instances to a list of dictionaries
        """
        predictions_dict = [prediction.__dict__ for prediction in predictions]

        return make_response({'predictions': predictions_dict}, 200)

    @staticmethod
    def _validate_member_id(member_id: Any, parameter_name: str = 'memberId') -> int:
        if not member_id:
            raise BadRequestHttpError(f'Missing {parameter_name} parameter')
        try:
            member_id = int(member_id)
        except ValueError:
            raise BadRequestHttpError(f'{parameter_name} must be a valid int')

        return member_id
