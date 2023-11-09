from django.urls import path
from .views import TestView

urlpatterns = [path("test/upload/", TestView.as_view())]
