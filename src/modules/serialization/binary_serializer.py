import pickle

from pathlib import Path
from typing import TypeVar


T = TypeVar("T")


class BinarySerializer:
    """
    A static utility class for serializing and deserializing Python objects
    to and from binary files using the standard 'pickle' module.
    """

    @staticmethod
    def serialize(path: str, data: object) -> None:
        """
        Serializes a Python object to a binary file using 'pickle.dump'.

        It ensures the parent directory of the specified path exists before writing.

        Args:
            path: The full path to the binary file where the data will be saved.
            data: The Python object (data) to serialize.
        """
        # Ensure the directory structure exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Open the file in binary write mode ('wb') and pickle the data
        with open(path, "wb") as file:
            pickle.dump(data, file)

    @staticmethod
    def deserialize(path: str) -> T:
        """
        Deserializes a Python object from a binary file using 'pickle.load'.

        Args:
            path: The full path to the binary file to read from.

        Returns:
            The deserialized Python object.
        
        Raises:
            FileNotFoundError: If the specified path does not exist.
            EOFError: If the file is empty or corrupt.
        """
        # Open the file in binary read mode ('rb') and unpickle the data
        with open(path, "rb") as file:
            # T is used to suggest that the return type matches the type that was saved
            return pickle.load(file)