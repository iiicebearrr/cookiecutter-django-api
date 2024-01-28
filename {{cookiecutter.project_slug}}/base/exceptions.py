from typing import Any

from .status_codes import (
    BODY_PARAM_MISSING,
    PATH_PARAM_MISSING,
    QUERY_PARAM_MISSING,
    UNCAUGHT_EXCEPTION,
    Code,
)


class CustomException(Exception):
    code: Code = UNCAUGHT_EXCEPTION

    def __init__(self, context: dict[str, Any] | None = None):
        self.context = context
        super().__init__(str(self))

    def __str__(self):
        return self.code.render(self.context)


class QueryParameterMissing(CustomException):
    code = QUERY_PARAM_MISSING


class PathParameterMissing(CustomException):
    code = PATH_PARAM_MISSING


class BodyParameterMissing(CustomException):
    code = BODY_PARAM_MISSING
