import json
import pickle
from pathlib import Path
from typing import Dict, NoReturn


def save_json(directory: Path,
              name: str,
              obj: object) -> NoReturn:
    with (directory / name).open('w') as file_out:
        file_out.write(json.dumps(obj, indent=4))


def load_json(directory: Path,
              name: str) -> Dict:
    with (directory / name).open('r') as read_file:
        return json.load(read_file)


def load_pickle(directory: Path,
                name: str) -> object:
    filepath = (directory / name)

    with filepath.open('rb') as file_input:
        return pickle.load(file_input)


def save_pickle(directory: Path,
                name: str,
                obj: object) -> NoReturn:
    with (directory / name).open('wb') as output:
        pickle.dump(obj, output)
