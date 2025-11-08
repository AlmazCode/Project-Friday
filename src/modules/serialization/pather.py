from pathlib import Path
from typing import Any, TypeVar, Optional, Union, Tuple

import json
import yaml
import os
import hashlib
import sys

from .binary_serializer import BinarySerializer


T = TypeVar("T")


class Pather:
    """
    A utility class for managing file paths, saving, loading, and serializing data.

    It handles paths relative to the project root, a dedicated save data directory,
    and provides methods for file operations like saving, reading, removing, and
    loading JSON/YAML data. It uses SHA256 hashing for internal filenames to
    avoid issues with special characters or path length limits.
    """

    WORK_DIR: str
    SAVE_DATA_PATH: str
    STARTUP_PATH: str

    @staticmethod
    def save(filename: str, data: object) -> None:
        """
        Saves an object to a file in the save data directory after serialization.

        The actual filename on disk is the SHA256 hash of the provided `filename`.
        Directories are created if they don't exist.

        Args:
            filename: The logical name of the file (used to generate the hash).
            data: The object to be serialized and saved.
        """
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(Pather.SAVE_DATA_PATH, file_hash)

        Path(Pather.SAVE_DATA_PATH).mkdir(parents=True, exist_ok=True)
        BinarySerializer.serialize(file_path, data)

    @staticmethod
    def read(filename: str, default: Optional[T] = None) -> Optional[T]:
        """
        Reads and deserializes data from a file in the save data directory.

        Args:
            filename: The logical name of the file (used to generate the hash).
            default: The value to return if the file does not exist. Defaults to None.

        Returns:
            The deserialized object, or the default value if the file is not found.
        """
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(Pather.SAVE_DATA_PATH, file_hash)

        if not os.path.exists(file_path):
            return default

        # Assumes BinarySerializer.deserialize returns a type compatible with T
        return BinarySerializer.deserialize(file_path)

    @staticmethod
    def read_and_remove(filename: str, default: Optional[T] = None) -> Optional[T]:
        """
        Reads and deserializes data from a file, then removes the file.

        This is useful for 'consume-once' data.

        Args:
            filename: The logical name of the file (used to generate the hash).
            default: The value to return if the file does not exist. Defaults to None.

        Returns:
            The deserialized object, or the default value if the file is not found.
        """
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(Pather.SAVE_DATA_PATH, file_hash)

        if not os.path.exists(file_path):
            return default

        # Assumes BinarySerializer.deserialize returns a type compatible with T
        value = BinarySerializer.deserialize(file_path)
        os.remove(file_path)
        return value

    @staticmethod
    def remove(filename: str) -> None:
        """
        Removes a specific file from the save data directory.

        Args:
            filename: The logical name of the file to remove (used to generate the hash).
        """
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(Pather.SAVE_DATA_PATH, file_hash)

        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def remove_all(*exceptions: str) -> None:
        """
        Removes all files in the save data directory, except for specified exceptions.

        Args:
            *exceptions: Variable number of logical filenames to keep (not remove).
        """
        if os.path.exists(Pather.SAVE_DATA_PATH):
            # Calculate hashes for files that should NOT be deleted
            exception_hashes = {Pather.string_to_sha256(fn) for fn in exceptions}

            for file in os.listdir(Pather.SAVE_DATA_PATH):
                file_path = os.path.join(Pather.SAVE_DATA_PATH, file)
                # 'file' here is the actual hash name on disk
                if file not in exception_hashes:
                    os.remove(file_path)

    @staticmethod
    def load_json(path: str) -> Any:
        """
        Loads data from a JSON file located relative to the WORK_DIR.

        Args:
            path: The relative path to the JSON file.

        Returns:
            The content of the JSON file as a Python object.
        """
        with open(Pather.collect_path(path), "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_yaml(path: str) -> Any:
        """
        Loads data from a YAML file located relative to the WORK_DIR.

        Args:
            path: The relative path to the YAML file.

        Returns:
            The content of the YAML file as a Python object.
        """
        with open(Pather.collect_path(path), "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def has(filename: str) -> bool:
        """
        Checks if a file with the given logical name exists in the save data directory.

        Args:
            filename: The logical name of the file (used to generate the hash).

        Returns:
            True if the file exists, False otherwise.
        """
        file_hash = Pather.string_to_sha256(filename)
        file_path = os.path.join(Pather.SAVE_DATA_PATH, file_hash)
        return os.path.exists(file_path)

    @staticmethod
    def string_to_sha256(data: str) -> str:
        """
        Generates a SHA256 hash digest for a given string.

        Args:
            data: The input string.

        Returns:
            The 64-character hexadecimal SHA256 digest string.
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def get_project_root() -> str:
        """
        Attempts to determine the project's root directory.

        It assumes the script is run from a sub-directory and returns the parent of
        the directory containing the main execution file (`sys.argv[0]`).

        Returns:
            The absolute path of the estimated project root directory.
        """
        main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.dirname(main_dir)

    @staticmethod
    def collect_path(*paths: Union[str, Tuple[str, ...]]) -> str:
        """
        Joins path components starting from the WORK_DIR.

        Args:
            *paths: Variable number of path components to join.

        Returns:
            The fully joined absolute path.
        """
        return os.path.join(Pather.WORK_DIR, *paths)

# Set the working directory (assumed project root)
Pather.WORK_DIR = Pather.get_project_root()
# Set the path for persistent saved data
Pather.SAVE_DATA_PATH = Pather.collect_path("data", "saves")
# Set the path to the Windows Startup folder
Pather.STARTUP_PATH = os.path.join(
    os.getenv("APPDATA"),
    r"Microsoft\Windows\Start Menu\Programs\Startup"
)