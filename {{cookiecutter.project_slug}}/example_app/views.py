from base.views import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    ListViewWithPost,
    PartialUpdateView,
    UpdateView,
)
from django.http import HttpRequest
from django.views import View

from .models import PydanticUser, User


class ExampleListItems(ListView):
    model = User


class ExampleListItemsWithPost(ListViewWithPost):
    http_method_names = ["post"]
    model = User


class ExampleCreateItem(CreateView):
    model = User
    pydantic_model = PydanticUser


class ExampleUpdateItem(UpdateView):
    model = User
    pydantic_model = PydanticUser


class ExampleDeleteItem(DeleteView):
    model = User


class ExamplePartialUpdateItem(PartialUpdateView):
    model = User
    pydantic_model = PydanticUser


class ExampleDetailItem(DetailView):
    model = User


class ExampleUncaughtExceptionHandler(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        raise ValueError("test uncaught exception handler")
