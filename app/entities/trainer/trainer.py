from abc import ABC, abstractmethod


class Trainer(ABC):
    version: str = ''

    @abstractmethod
    def train(self):
        pass
