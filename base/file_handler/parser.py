import abc
import requests
from typing import BinaryIO, Iterable
from django.http import HttpRequest
from pydantic import HttpUrl
from django.core.files.base import File
from functools import cached_property


class BaseFileParser(abc.ABC):
    chunk_size = 64 * 2**10

    def __init__(self, request: HttpRequest, **kwargs):
        self.request = request

    @abc.abstractmethod
    def parse(self, *args, **kwargs) -> Iterable[bytes]:
        pass


class StreamFileParser(BaseFileParser):
    file_field: str = "file"

    @cached_property
    def file(self) -> File:
        return self.get_file()

    @cached_property
    def chunks(self) -> Iterable[bytes]:
        return self.file.chunks(chunk_size=self.chunk_size)

    def get_file(self) -> File:
        return self.request.FILES[self.file_field]  # type: ignore

    def parse(self, *args, **kwargs) -> Iterable[bytes]:
        yield from self.chunks


class OssFileParser(BaseFileParser):
    url_field = "url"

    @cached_property
    def url(self) -> HttpUrl:
        return self.get_url()

    @cached_property
    def chunks(self) -> Iterable[bytes]:
        return self.get_chunks()

    def get_url(self) -> HttpUrl:
        url: str = self.request.POST[self.url_field]  # type: ignore
        return HttpUrl(url)

    def send_request(self, method: str = "get", **request_kwargs) -> requests.Response:
        return requests.request(method, str(self.url), **request_kwargs)

    def get_chunks(self) -> Iterable[bytes]:
        resp = self.send_request(stream=True)
        return resp.iter_content(chunk_size=self.chunk_size)

    def parse(self, *args, **kwargs) -> Iterable[bytes]:
        yield from self.chunks


class AwsFileParser(OssFileParser):
    pass
