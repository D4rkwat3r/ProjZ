from ..api_exception import APIException


class IncorrectVerificationCode(APIException):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            code=kwargs["code"],
            message=kwargs["message"]
        )
