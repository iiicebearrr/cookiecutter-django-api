import json
from typing import Any

from django.core.paginator import Paginator
from django.db import models
from django.forms.models import model_to_dict
from django.http.response import JsonResponse

from .status_codes import SUCCESS


class Response(JsonResponse):
    def serialize_model_data(self, data: Any) -> Any:
        match data:
            case bytes():
                return json.loads(data.decode())
            case str() | int() | float() | bool() | None | dict():
                return data
            case models.Model():
                return model_to_dict(data)
            case models.query.QuerySet():
                return data.values()
            case list() | tuple():
                return [self.serialize_model_data(item) for item in data]
            case _:
                return data

    def __init__(self, data: Any, msg: str | None = None, **kwargs):
        super().__init__(
            {
                "data": self.serialize_model_data(data),
                "msg": msg,
                "code": SUCCESS.code,
            },
            **kwargs,
        )


class PaginatedResponse(Response):
    def __init__(
        self,
        data: list[Any] | None = None,
        count: int = 0,
        paginator: Paginator | None = None,
        **kwargs,
    ):
        if paginator is not None and isinstance(paginator, Paginator):
            super().__init__(
                {
                    "list": list(paginator.object_list.values()),
                    "count": paginator.count,
                },
                **kwargs,
            )
        else:
            super().__init__({"list": data, "count": count}, **kwargs)
