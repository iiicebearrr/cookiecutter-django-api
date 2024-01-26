import json
import typing

from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import model_to_dict
from django.views import generic, View
from django.http import HttpRequest
from functools import cached_property

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

    @cached_property
    def filter_backend(self) -> FilterBackendBase:
        return self.filter_backend_class(self.request, self.model)

    def get_paginate_by(self, queryset: QuerySet) -> int:
        return self.request.GET.get(self.size_kwarg, 10)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.filter_backend is not None:
            queryset = self.filter_backend.filter_queryset(queryset)
        return queryset

    def get(self, request: HttpRequest, *args, **kwargs):
        qs = self.get_queryset()
        self.object_list = self.filter_queryset(qs)
        context = super().get_context_data(**kwargs)
        paginator = context["paginator"]
        if paginator is None:
            return Response(data=context["object_list"])
        return PaginatedResponse(paginator=context["paginator"])


class ListViewWithPost(ListView):
    filter_backend_class = BodyParamsFilterBackend

    def post(self, request, *args, **kwargs):
        """Post query"""
        # self._filter_backend = BodyParamsFilterBackend(request, self.model)
        return self.get(request, *args, **kwargs)


class ObjectMixin:
    model: Model
    ret_model_fields: list[str] | None = None
    ret_model_fields_exclude: list[str] | None = None

    def __init__(self):
        self.object: Model | None = None

    def return_inst(self, instance: Model | None = None) -> Response:
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
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.return_inst()


class CreateView(ValidateObjectMixin, View):
    """Using pydantic as data validation"""

    def post(self, request, *args, **kwargs):
        self.object = self.perform_create(self.validate(request))
        return self.return_inst()

    def perform_create(self, data: dict) -> Model:
        return self.model.objects.create(**data)


class UpdateMixinView(generic.detail.SingleObjectMixin, ValidateObjectMixin, View):
    def perform_update(self, instance: Model, partial: bool = False) -> Model:
        for k, v in self.validate(self.request, partial=partial).items():
            setattr(instance, k, v)

        instance.save()
        return instance


class UpdateView(UpdateMixinView):
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.perform_update(self.object)
        return self.return_inst()


class PartialUpdateView(UpdateMixinView):
    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.perform_update(self.object, partial=True)
        return self.return_inst()


class DeleteView(generic.detail.SingleObjectMixin, ObjectMixin, View):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.perform_delete()
        return Response(data="success")

    def perform_delete(self):
        self.object.delete()


class UploadView(View):
    # TODO: parse file content from stream or oss to bytes-like object
    parsers: list = []

    def get_upload_resource(self):
        # Get bytes-like object from self.parsers
        raise NotImplementedError()

    def perform_upload(self):
        # Save bytes-like object to database or somewhere
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class DownloadView(View):
    # TODO: load content from database or somewhere
    loaders: list = []

    def get_download_resource(self):
        # Get content from self.loaders
        raise NotImplementedError()

    def perform_download(self):
        # Serialize content to bytes-like object
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        raise NotImplementedError()
