import typing

from django.db.models import Model
from django.db.models.query import QuerySet
from django.http.request import HttpRequest


class FilterBackendBase:
    fields: list[str] | None = None

    def __init__(self, request: HttpRequest, model: Model):
        self.request = request
        self.model = model
        self._allow_fields: list[str] | None = None

    @property
    def allow_fields(self) -> list[str]:
        if self._allow_fields is None:
            self._allow_fields = self.get_filter_fields()
        return self._allow_fields

    def filter_queryset(self, queryset: QuerySet):
        return queryset.filter(**self.get_allow_query_params())

    def get_filter_fields(self) -> list[str]:
        if self.fields is None:
            return [field.name for field in self.model._meta.fields]
        return self.fields

    def get_query_params(self) -> dict[str, typing.Any]:
        return self.request.GET.dict()

    def get_allow_query_params(self) -> dict[str, typing.Any]:
        return {
            key: value
            for key, value in self.get_query_params().items()
            if key in self.allow_fields
        }


class QueryParamsFilterBackend(FilterBackendBase):

    """Filter queryset by query params."""


class BodyParamsFilterBackend(FilterBackendBase):

    """Filter queryset by body params."""

    def get_query_params(self) -> dict[str, typing.Any]:
        return self.request.POST.dict()
