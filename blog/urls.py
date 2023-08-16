from django.urls import path
from . import views

urlpatterns = [
    path("", views.BlogsView.as_view(), name="blogs-list"),
    path("/<int:id>", views.BlogsDetailView.as_view(), name="blogs-detail"),
    path("/<int:id>/edit", views.BlogsEditView.as_view(), name="blogs-edit"),
    path("/<int:id>/publish", views.publish_post, name="blogs-publish"),
]
