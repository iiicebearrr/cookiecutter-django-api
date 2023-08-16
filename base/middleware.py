import json
import logging
from itertools import groupby, chain

from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django.http.response import HttpResponse

# from django.db.models.query
from pydantic import ValidationError

from . import status_codes
from .exceptions import CustomException

# from .status_codes import (
#     UNCAUGHT_EXCEPTION,
#     FAILED,
#     PYDANTIC_VALIDATION_ERROR,
#     OBJECT_NOT_FOUND,
# )

logger = logging.getLogger("django")


class BaseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response: HttpResponse = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class ExceptionMiddleware(BaseMiddleware):
    def __call__(self, *args, **kwargs):
        response: HttpResponse = super().__call__(*args, **kwargs)
        if response.status_code >= 400:
            msg = status_codes.FAILED.render(
                {
                    "status_code": response.status_code,
                    "msg": str(response),
                }
            )

            logger.error(msg)
            return HttpResponse(
                json.dumps(
                    {
                        "data": None,
                        "msg": msg,
                        "code": response.status_code,
                    }
                )
            )
        return response

    def dispatch_exception(self, exception: Exception) -> tuple[str, int]:
        # TODO: Exception on validation/database constraint/object not found
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

        # Uncaught exception
        return (
            status_codes.UNCAUGHT_EXCEPTION.render({"msg": str(exception)}),
            status_codes.UNCAUGHT_EXCEPTION.code,
        )

    def process_exception(self, request: HttpRequest, exception: Exception):
        msg, code = self.dispatch_exception(exception)
        logger.error(msg, exc_info=True)
        return HttpResponse(json.dumps({"data": None, "msg": msg, "code": code}))


class LoggingMiddleware(BaseMiddleware):
    ...
