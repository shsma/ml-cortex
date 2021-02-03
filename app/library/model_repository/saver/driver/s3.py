import tempfile
import pickle
import json
import os
from pathlib import Path
from typing import NoReturn, Dict
from app.entities.model.model import Model
from app.library.model_repository.repository import Repository
from app.library.model_repository.saver.saver_interface import SaverInterface
from git import Repo
from pandas import DataFrame
import tarfile
from boto3_type_annotations.s3 import Client


class S3(SaverInterface):

    _GIT_REPO_NAME = "ml-brand-gender"
    _METADATA_FILENAME = "metadata.json"
    _TAR_FILE_NAME = "model.tar"
    repo_config: Repository = None
    s3_client: None
    s3_bucket: str = None

    def __init__(self, repo_config: Repository, s3_client: Client, s3_bucket: str):
        """Initialize the class with basic path and file names"""
        self.repo_config = repo_config
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket

    def save_model(self, model: Model) -> NoReturn:

        model_info = model.to_model_info()

        path = self.repo_config.build_path_from_info(model_info)

        self._save_tar(path,
                       metadata=self._build_metadata(),
                       model=model
                       )

    def _build_metadata(self) -> Dict[str, str]:
        repo = Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return {
            "repository": self._GIT_REPO_NAME,
            "trunk": "master",
            "sha": str(sha)
        }

    def _save_tar(self, path: Path, metadata: Dict, model: Model) -> NoReturn:
        """Save model and metadata to file, compress it into a tar file an upload it to s3"""
        model_file_name = self.repo_config.model_file_name

        try:
            # Create a tmp directory
            with tempfile.TemporaryDirectory() as tmp_path:
                os.chdir(tmp_path)

                # Save to file the dat
                with open(model_file_name, 'wb') as f:
                    pickle.dump(model, f)

                with open(self._METADATA_FILENAME, 'w') as f:
                    json.dump(metadata, f)

                # Tar the tmp directory with all the files
                with tarfile.open(self._TAR_FILE_NAME, "w") as tar:
                    for file in os.listdir(tmp_path):
                        tar.add(file)

                # Upload the tar file to S3
                s3_file_path = str(Path(str(path) + '/' + self._TAR_FILE_NAME))
                tmp_file_path = tmp_path + '/' + self._TAR_FILE_NAME
                self.s3_client.upload_file(tmp_file_path, self.s3_bucket, s3_file_path)
        finally:
            del tmp_path
