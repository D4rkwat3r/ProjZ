from ..api_exception import APIException


class InvalidEmail(APIException):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            code=kwargs["code"],
            message=kwargs["message"]
        )
