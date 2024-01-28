from django.urls import path
from .views import (
    ExampleListItems,
    ExampleListItemsWithPost,
    ExampleCreateItem,
    ExampleUpdateItem,
    ExampleDeleteItem,
    ExamplePartialUpdateItem,
    ExampleDetailItem,
)

urlpatterns = [
    path("list", ExampleListItems.as_view()),
    path("list_with_post", ExampleListItemsWithPost.as_view()),
    path("create", ExampleCreateItem.as_view()),
    path("update/<int:pk>", ExampleUpdateItem.as_view()),
    path("delete/<int:pk>", ExampleDeleteItem.as_view()),
    path("partial_update/<int:pk>", ExamplePartialUpdateItem.as_view()),
    path("detail/<int:pk>", ExampleDetailItem.as_view()),
    path("error", lambda request: 1 / 0),
]
