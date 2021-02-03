import abc
from pandas import DataFrame
from app.entities.model.model_info import ModelInfo
from app.entities.model.model import Model


class LoaderInterface(abc.ABC):

    @abc.abstractmethod
    def load_model(self, model_info: ModelInfo) -> Model:
        pass

    @abc.abstractmethod
    def load_data(self, model_info: ModelInfo) -> DataFrame:
        pass
