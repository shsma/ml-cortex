import pickle
from pathlib import Path
from pandas import DataFrame
from typing import Union
from app.entities.model.model_info import ModelInfo
from app.library.model_repository.loader.loader_interface import LoaderInterface
from app.entities.model.model import Model
from app.library.model_repository.repository import Repository
from app.errors import ApplicationException


class Filesystem(LoaderInterface):
    """Filesystem Model and Data loader"""

    repo_config: Repository = None

    def __init__(self, repo_config: Repository):
        """Initialize the class with basic path and file names"""
        self.repo_config = repo_config

    def load_model(self, model_info: ModelInfo) -> Model:
        """Load the model artifact from local filesystem"""
        path = self.repo_config.build_path_from_info(model_info, self.repo_config.model_file_name)
        return self._load_artifact_file(path)

    def load_data(self, model_info: ModelInfo) -> DataFrame:
        """Load the data artifact from local filesystem"""
        path = self.repo_config.build_path_from_info(model_info, self.repo_config.data_file_name)
        return self._load_artifact_file(path)

    @staticmethod
    def _load_artifact_file(file_location: Path) -> Union[DataFrame, Model]:
        """Load artifact from path.
        Contain logic to un-serialize the file"""
        with file_location.open('rb') as artifact_file:
            artifact = pickle.load(artifact_file)
            if artifact is None:
                raise ApplicationException("Artifact loaded from '{}' is None".format(file_location))
            return artifact
