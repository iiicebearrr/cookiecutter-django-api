import json
from functools import wraps

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest

from .exceptions import QueryParameterMissing, BodyParameterMissing


def _get_request(*args) -> HttpRequest:
    view, *request = args
    if not request:
        request: HttpRequest = view
    else:
        request: HttpRequest = request[0]
    return request


def query_params(*parameters: str):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            request = _get_request(*args)
            for parameter in parameters:
                if parameter not in request.GET:
                    raise QueryParameterMissing(context={"param": parameter})
            return func(*args, **kwargs)

        return inner

    return wrapper


def body_params(*body: str):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            request = _get_request(*args)

            if request.method != "POST":
                loc = json.loads(request.body)
            else:
                loc = request.POST
            for parameter in body:
                if parameter not in loc:
                    raise BodyParameterMissing(context={"param": parameter})
            return func(*args, **kwargs)

        return inner

    return wrapper


def superuser_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if settings.DEBUG:
            return func(*args, **kwargs)
        request = _get_request(*args)
        if any(
            [
                not request.user,
                isinstance(request.user, AnonymousUser),
                not isinstance(request.user, User),
                not request.user.is_superuser,
            ]
        ):
            raise PermissionDenied("Superuser required")
        return func(*args, **kwargs)

    return inner


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if settings.DEBUG:
            return func(*args, **kwargs)
        request = _get_request(*args)
        if any(
            [
                not request.user,
                isinstance(request.user, AnonymousUser),
                not isinstance(request.user, User),
                not request.user.is_authenticated,
            ]
        ):
            raise PermissionDenied("Login required")
        return func(*args, **kwargs)

    return inner
