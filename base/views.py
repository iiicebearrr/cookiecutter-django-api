import typing
import json
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import model_to_dict
from django.views import generic, View
from pydantic import BaseModel

from .filter_backends import (
    QueryParamsFilterBackend,
    BodyParamsFilterBackend,
    FilterBackendBase,
)
from .response import Response, PaginatedResponse


class ListView(generic.ListView):
    size_kwarg: str = "size"
    default_size: int = 10
    filter_backend_class: typing.Type[
        FilterBackendBase
    ] | None = QueryParamsFilterBackend
    ordering = ("-create_at",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list: QuerySet | None = None
        self._filter_backend: FilterBackendBase | None = None

    @property
    def filter_backend(self) -> FilterBackendBase:
        if self._filter_backend is None:
            self._filter_backend = self.filter_backend_class(self.request, self.model)
        return self._filter_backend

    def get_paginate_by(self, queryset: QuerySet) -> int:
        return self.request.GET.get("size", 10)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.filter_backend is not None:
            queryset = self.filter_backend.filter_queryset(queryset)
        return queryset

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        self.object_list = self.filter_queryset(qs)
        context = super().get_context_data(**kwargs)
        paginator = context["paginator"]
        if paginator is None:
            return Response(data=context["object_list"])
        return PaginatedResponse(paginator=context["paginator"])


class ListViewWithPost(ListView):
    def post(self, request, *args, **kwargs):
        """Post query"""
        self._filter_backend = BodyParamsFilterBackend(request, self.model)
        return self.get(request, *args, **kwargs)


class ObjectMixin:
    model: Model
    ret_model_fields: list[str] | None = None
    ret_model_fields_exclude: list[str] | None = None

    def __init__(self):
        self.object: Model | None = None

    def responder(self, instance: Model | None = None) -> Response:
        instance = instance or self.object
        if instance is None:
            raise ValueError("instance is None")
        return Response(
            data=model_to_dict(
                instance,
                fields=self.ret_model_fields,
                exclude=self.ret_model_fields_exclude,
            )
        )


class ValidateObjectMixin(ObjectMixin):
    pydantic_model: typing.Type[BaseModel] | None = None

    def validate(self, request, partial: bool = False) -> dict[str, typing.Any]:
        if request.method != "POST":
            loc = json.loads(request.body.decode())
        else:
            loc = request.POST.dict()

        if self.pydantic_model is not None:
            if not partial:
                return self.pydantic_model(**loc).model_dump()

            # For partial update
            return self.pydantic_model(
                **model_to_dict(self.object),
                **loc,
            ).model_dump()
        return loc


class DetailView(generic.detail.SingleObjectMixin, ObjectMixin, View):
    pk_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.responder()


class CreateView(ValidateObjectMixin, View):
    """Using pydantic as data validation"""

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.create(**self.validate(request))
        return self.responder()


class UpdateView(generic.detail.SingleObjectMixin, ValidateObjectMixin, View):
    pk_url_kwarg = "id"

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        for k, v in self.validate(request).items():
            setattr(self.object, k, v)
        self.object.save()
        return self.responder()


class PartialUpdateView(generic.detail.SingleObjectMixin, ValidateObjectMixin, View):
    pk_url_kwarg = "id"

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        for k, v in self.validate(request, partial=True).items():
            setattr(self.object, k, v)
        self.object.save()
        return self.responder()


class DeleteView(generic.detail.SingleObjectMixin, ObjectMixin, View):
    pk_url_kwarg = "id"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return Response(data="success")
