from abc import ABC, abstractmethod
from datetime import datetime

from app.entities.model.model_info import ModelInfo
from app.entities.model.prediction import Prediction


class Model(ABC):
    version: str = None
    USE_CASE = 'BRAND_GENDER'

    def __init__(self):
        self.init_date = datetime.now()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def predict(self, data) -> Prediction:
        pass

    def to_model_info(self) -> ModelInfo:
        return ModelInfo(
            usecase=self.USE_CASE,
            model=self.name,
            version=self.version,
            timestamp=self.init_date.strftime('%Y-%m-%d-%H-%M-%S')
        )
