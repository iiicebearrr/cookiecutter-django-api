from django.utils.translation import gettext_lazy as _


class Code:
    def __init__(self, msg: str, code: int = 0):
        self.msg = msg
        self.code = code

    def render(self, context: dict[str, str] | None = None) -> str:
        return _("[%(code)s] %(msg)s") % {
            "code": self.code,
            "msg": self.msg % context if context is not None else self.msg,
        }


SUCCESS = Code("Success", 0)
UNCAUGHT_EXCEPTION = Code("Error: %(msg)s", 1)
FAILED = Code("Response failed with %(status_code)s: %(msg)s", 2)
QUERY_PARAM_MISSING = Code("Query param `%(param)s` is required", 3)
BODY_PARAM_MISSING = Code("Body param `%(param)s` is required", 4)
PYDANTIC_VALIDATION_ERROR = Code("Validation error: %(msg)s", 5)
OBJECT_NOT_FOUND = Code("Object not found: %(msg)s", 6)
PATH_PARAM_MISSING = Code("Path param `%(param)s` is required", 7)
LOGIN_REQUIRED = Code("Login required", 8)
