from ..api_exception import APIException


class CaptchaCaught(APIException):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            code=kwargs["code"],
            message=kwargs["message"]
        )
        self.redirect_url = kwargs["url"]
