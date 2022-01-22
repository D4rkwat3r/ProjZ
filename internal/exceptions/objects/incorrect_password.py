from ..api_exception import APIException


class IncorrectPassword(APIException):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs["code"],
            kwargs["message"]
        )
