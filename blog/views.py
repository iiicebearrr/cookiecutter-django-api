import typing

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.views.decorators.http import require_http_methods

from base.decorators import superuser_required
from base.exceptions import PathParameterMissing
from base.response import Response
from base.views import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Blogs
from .validators import PydanticPost


class BlogsView(ListView, CreateView):
    model = Blogs

    def validate(self, request, partial: bool = False) -> dict[str, typing.Any]:
        base_data = super().validate(request, partial=partial)

        return {
            **base_data,
            # TODO: Authenticated user
            **{
                "author": User.objects.get_or_create(
                    username="administrator",
                    password="administrator",
                    is_superuser=True,
                )[0]
            },
        }

    @superuser_required
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BlogsDetailView(DetailView):
    model = Blogs


class BlogsEditView(UpdateView, DeleteView):
    model = Blogs

    pydantic_model = PydanticPost

    ret_model_fields_exclude = ["content"]

    @superuser_required
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @superuser_required
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@require_http_methods(["POST"])
@superuser_required
def publish_post(request: HttpRequest, **kwargs):
    pk = kwargs.get("id")
    if not pk:
        raise PathParameterMissing({"param": "id"})
    inst = Blogs.objects.get(id=pk)

    inst.published = True

    inst.save()

    return Response(data="success")
