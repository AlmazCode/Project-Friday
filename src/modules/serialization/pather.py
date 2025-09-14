from .binary_serializer import BinarySerializer

import json
import yaml
import os
import hashlib
import sys

from pathlib import Path
from typing import Any, TypeVar, Optional


T = TypeVar("T")


class Pather:

    @staticmethod
    def save(filename: str, data: object) -> None:
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(SAVE_DATA_PATH, file_hash)

        Path(SAVE_DATA_PATH).mkdir(parents=True, exist_ok=True)
        BinarySerializer.serialize(file_path, data)

    @staticmethod
    def read(filename: str, default: Optional[T] = None) -> Optional[T]:
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(SAVE_DATA_PATH, file_hash)

        if not os.path.exists(file_path):
            return default

        return BinarySerializer.deserialize(file_path)

    @staticmethod
    def read_and_remove(filename: str, default: Optional[T] = None) -> Optional[T]:
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(SAVE_DATA_PATH, file_hash)

        if not os.path.exists(file_path):
            return default

        value = BinarySerializer.deserialize(file_path)
        os.remove(file_path)
        return value

    @staticmethod
    def remove(filename: str) -> None:
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(SAVE_DATA_PATH, file_hash)

        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def remove_all(*exceptions: str) -> None:
        if os.path.exists(SAVE_DATA_PATH):
            exception_hashes = {Pather.string_to_sha256(fn) for fn in exceptions}

            for file in os.listdir(SAVE_DATA_PATH):
                file_path = os.path.join(SAVE_DATA_PATH, file)
                if file not in exception_hashes:
                    os.remove(file_path)
    
    @staticmethod
    def load_json(path: str) -> Any:
        with open(Pather.collect_path(path), "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def load_yaml(path: str) -> Any:
        with open(Pather.collect_path(path), "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def has(filename: str) -> bool:
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(SAVE_DATA_PATH, file_hash)
        return os.path.exists(file_path)

    @staticmethod
    def string_to_sha256(data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    
    @staticmethod
    def get_project_root():
        main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.dirname(main_dir)

    @staticmethod
    def collect_path(*paths) -> str:
        return os.path.join(WORK_DIR, *paths)


WORK_DIR = Pather.get_project_root()
SAVE_DATA_PATH: str = Pather.collect_path("data", "saves")
STARTUP_PATH: str = os.path.join(
    os.getenv("APPDATA"),
    r"Microsoft\Windows\Start Menu\Programs\Startup"
)