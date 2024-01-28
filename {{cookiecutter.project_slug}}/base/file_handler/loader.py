import abc
from typing import Any

from pydantic import HttpUrl


class Uploader(abc.ABC):
    pass


class AWSUploader(Uploader):
    pass


class BaseFileLoader(abc.ABC):
    chunk_size = 64 * 2**10
    uploader: Uploader = AWSUploader

    @abc.abstractmethod
    def load(
        self, path: Any = None, content: bytes | None = None, upload: bool = False
    ) -> bytes | HttpUrl:
        """

        :param path: file path
        :param content: file content
        :param upload: True: upload file to oss using `self.uploader`, and return a `HttpUrl` object. False: return file content
        :return:
        """
        ...
