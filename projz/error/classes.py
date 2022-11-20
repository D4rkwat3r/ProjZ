from typing import Optional


class ApiException(Exception):

    errors = {}

    def __init__(self, code: int, message: str, *args, **kwargs):
        self.code = code
        self.message = message
        super().__init__(self.message)

    @classmethod
    def create(cls, code: int, extras: Optional[dict[str, str]] = None):
        def decorator(clazz: type):
            def init_wrapper(instance, message: str, response: Optional[dict] = None):
                if response is None: response = dict()
                cls.__init__(instance, code, message, response)
                if extras is not None:
                    for extra in extras: setattr(instance, extras[extra], response.get(extra))
            clazz.__init__ = init_wrapper
            cls.errors[code] = clazz
            return clazz
        return decorator

    @classmethod
    def get(cls, response: dict) -> "ApiException":
        code = response.get("apiCode") or -1
        message = response.get("apiMsg") or ""
        found_error = (cls.errors.get(code) or cls)
        if found_error is ApiException:
            return ApiException(code, message)
        return found_error(message, response)


@ApiException.create(-1)
class BadResponse(ApiException): ...


@ApiException.create(2009)
class InvalidEmail(ApiException): ...


@ApiException.create(1008, extras={"redirectUrl": "url"})
class CaptchaCaught(ApiException): ...
