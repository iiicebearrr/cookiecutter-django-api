import logging
from itertools import chain, groupby

from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from pydantic import ValidationError

from . import status_codes
from .exceptions import CustomException
from .response import ResponseStructure

logger = logging.getLogger("default")


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response: HttpResponse = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class JsonMiddleware(BaseMiddleware):
    def __call__(self, *args, **kwargs) -> HttpResponse:
        response: HttpResponse = super().__call__(*args, **kwargs)
        if response.status_code >= 400:
            detail = response.reason_phrase

            msg = status_codes.FAILED.render(
                {"status_code": response.status_code, "msg": detail}
            )

            logger.error(msg)
            r = ResponseStructure(
                data=None,
                msg=msg,
                code=response.status_code,
            )
            return HttpResponse(
                r.model_dump_json(by_alias=True),
            )
        return response

    @staticmethod
    def dispatch_exception(exception: Exception) -> tuple[str, int]:
        # Custom exception raised by views
        if isinstance(exception, CustomException):
            return str(exception), exception.code.code

        # Database object not found
        if isinstance(exception, ObjectDoesNotExist):
            return (
                status_codes.OBJECT_NOT_FOUND.render({"msg": str(exception)}),
                status_codes.OBJECT_NOT_FOUND.code,
            )

        # Data validation using pydantic
        if isinstance(exception, ValidationError):
            err_msgs = []
            for err_type, err_list in groupby(exception.errors(), lambda x: x["msg"]):
                err_list = list(err_list)
                err_msgs.append(
                    f"{err_type}: {list(chain.from_iterable([err['loc'] for err in err_list]))}"
                )
            return ", ".join(err_msgs), status_codes.PYDANTIC_VALIDATION_ERROR.code

        # TODO: Database constraint violation

        # Uncaught exception
        return (
            status_codes.UNCAUGHT_EXCEPTION.render({"msg": str(exception)}),
            status_codes.UNCAUGHT_EXCEPTION.code,
        )

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse:
        msg, code = self.dispatch_exception(exception)
        logger.error(msg, exc_info=True)
        r = ResponseStructure(
            data=None,
            msg=msg,
            code=code,
        )
        return HttpResponse(r.model_dump_json(by_alias=True))
