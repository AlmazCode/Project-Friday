import pickle
from pathlib import Path


class BinarySerializer:
    @staticmethod
    def serialize(path: str, data: object) -> None:
        """
        Serialize data to binary file.
        :param path: Path to file.
        :param data: Data to serialize.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as file:
            pickle.dump(data, file)

    @staticmethod
    def deserialize(path: str):
        """
        Deserialize data from binary file.
        :param path: Path to file.
        :return: Deserialized data.
        """
        with open(path, "rb") as file:
            return pickle.load(file)
