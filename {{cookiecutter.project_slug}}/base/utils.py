import typing

from django.db import models
from django.http.request import HttpRequest
from rich import print

from .exceptions import QueryParameterMissing


def log_settings(settings: str):
    print(f"[green bold]Using {settings} settings[/]")


class ObjectFinder:
    def __init__(
        self,
        model: typing.Type[models.Model],
        request: HttpRequest | None = None,
    ):
        self.request = request
        self.model = model

    def get_object(self, **kwargs) -> models.Model:
        if not kwargs:
            raise ValueError("Query kwargs must be provided")
        return self.model.objects.get(**kwargs)

    def get_by_pk(self, pk: typing.Any, pk_field: str = "pk") -> models.Model:
        if pk is None:
            raise QueryParameterMissing(
                {
                    "param": pk_field,
                }
            )
        return self.get_object(**{pk_field: pk})

    def get_by_request(self, pk_field: str = "pk"):
        return self.get_by_pk(self.request.GET.get(pk_field))
