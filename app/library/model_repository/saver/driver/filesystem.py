import pickle
import os
from pathlib import Path
from typing import NoReturn, Union
from app.library.model_repository.saver.saver_interface import SaverInterface
from app.entities.model.model import Model
from app.library.model_repository.repository import Repository
from pandas import DataFrame


class Filesystem(SaverInterface):

    repo_config: Repository = None

    def __init__(self, repo_config: Repository):
        """Initialize the class with basic path and file names"""
        self.repo_config = repo_config

    def save_model(self, model: Model) -> NoReturn:
        """Save the model in the local directory"""
        model_info = model.to_model_info()
        path = self.repo_config.build_path_from_info(model_info)

        # Save model
        self._save(path, self.repo_config.model_file_name, model)

    @staticmethod
    def _create_local_dir(path: Path) -> NoReturn:
        """Create the local directory if does not exist"""
        if not os.path.exists(str(path)):
            os.makedirs(str(path))

    @staticmethod
    def _save(path: Path, file_name: str, instance: Union[DataFrame, Model]) -> NoReturn:
        """Save into a pkl file the instance passed"""

        Filesystem._create_local_dir(path)
        with (path / file_name).open('wb') as file_handler:
            pickle.dump(instance, file_handler)
