import abc
from datetime import datetime
from app.entities.model.model import Model
from pandas import DataFrame
from typing import NoReturn


class SaverInterface(abc.ABC):

    @abc.abstractmethod
    def save_model(self, model: Model) -> NoReturn:
        pass
