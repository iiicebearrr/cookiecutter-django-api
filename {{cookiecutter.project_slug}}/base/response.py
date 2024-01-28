import json
from typing import Any

from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from pydantic import BaseModel, Field

from .status_codes import SUCCESS

RESPONSE_CONFIG = settings.DJANGO_REST


class ResponseStructure(BaseModel):
    data: Any = Field(..., serialization_alias=RESPONSE_CONFIG["RESPONSE_DATA_FIELD"])
    msg: str | None = Field(
        None, serialization_alias=RESPONSE_CONFIG["RESPONSE_MESSAGE_FIELD"]
    )
    code: int = Field(
        SUCCESS.code, serialization_alias=RESPONSE_CONFIG["RESPONSE_CODE_FIELD"]
    )


class PaginatedResponseStructure(BaseModel):
    paginated_list: list[Any] = Field(
        [], serialization_alias=RESPONSE_CONFIG["RESPONSE_PAGINATED_LIST_FIELD"]
    )
    count: int = Field(
        0, serialization_alias=RESPONSE_CONFIG["RESPONSE_PAGINATED_COUNT_FIELD"]
    )


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

    def __init__(
        self, data: Any, msg: str | None = None, code: int | None = None, **kwargs
    ):
        self.response = ResponseStructure(
            data=self.serialize_model_data(data),
            msg=msg,
            code=code or SUCCESS.code,
        )
        super().__init__(
            self.response.model_dump(by_alias=True),
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
            self.paginate_response = PaginatedResponseStructure(
                paginated_list=list(paginator.object_list.values()),
                count=paginator.count,
            )

        else:
            self.paginate_response = PaginatedResponseStructure(
                paginated_list=data or [], count=count
            )

        super().__init__(
            data=self.paginate_response.model_dump(by_alias=True),
            **kwargs,
        )
