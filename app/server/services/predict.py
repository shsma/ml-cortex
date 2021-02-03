from typing import List
from ssense_logger.app_logger import AppLogger
from app.server.entities.prediction import Prediction
from app.entities.model.model import Model
from app.repositories.redis_repository import RedisRepository
from requests import post


class PredictService:
    _url = '';
    _model = None

    def __init__(
            self,
            app_logger: AppLogger,
            model: Model,
            customer_interaction_repository: RedisRepository
    ):
        self.app_logger = app_logger
        self._model = model
        self._customer_interaction_repository = customer_interaction_repository

    def predict(self, member_id: int, request_id: str) -> List[Prediction]:

        # Load user data
        user_data = self._customer_interaction_repository.get_by_member_id(member_id)
        if user_data.empty:
            self.app_logger.info(msg=f'{member_id} has no user interactions',
                                 tags=['PredictService', 'no_user_interactions'],
                                 request_id=request_id)
            return []

        # raw_predictions = self._model.predict(user_data)
        data = {
            'user_data': user_data
        }
        raw_predictions = post(self._url, data=data)
        if raw_predictions is None or len(raw_predictions.brand.keys()) < 1:
            self.app_logger.info(msg=f'{member_id} has no predictions', tags=['PredictService', 'no_predictions'],
                                 request_id=request_id)
            return []

        predictions = list(map(
            lambda k: Prediction(
                brand_id=raw_predictions.brand[k],
                gender=raw_predictions.gender[k],
                score=raw_predictions.score[k],
                liked=raw_predictions.liked[k]
            ), raw_predictions.brand.keys()))

        return predictions
