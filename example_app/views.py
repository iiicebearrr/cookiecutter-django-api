from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse

# Create your views here.


class TestView(View):
    def post(self, request):
        f = request.FILES["file"]
        print(type(f), f)
        return JsonResponse({"ok": True})
