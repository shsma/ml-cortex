from app.entities.model.model import ModelInfo
from pathlib import Path


class Repository:
    model_file_name = 'model.pkl'
    data_file_name = 'input_data.pkl'

    def __init__(self, base_dir: str):
        """This class define the repository structure for serialized model,
        It contain the file name for model and data.
        It and the logic to build the path of model and data"""

        self.base_dir = base_dir

    def build_path_from_info(self, model_info: ModelInfo, file_name=None) -> Path:
        """Build path from ModelInfo.
        Contain logic to build the file location"""
        parts = [self.base_dir,
                 model_info.usecase,
                 model_info.model,
                 model_info.version,
                 'latest',  # todo: replace with non-hardcoded string after we do cleanup logic
                 ]
        if file_name is not None:
            parts.append(file_name)

        return Path('/'.join(parts))
