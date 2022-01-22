from ..exceptions.other.response_received_error import ResponseReceivingError
from ujson import loads
from typing import Optional


class ZApiResponse:
    def __init__(self, payload: str) -> None:
        self.api_code: Optional[int] = None
        self.api_message: Optional[str] = None
        try:
            self.json = loads(payload)
        except ValueError:
            raise ResponseReceivingError("Malformed JSON received from Project Z API")
        self.is_request_succeed = False if "apiCode" in self.json else True
        if not self.is_request_succeed:
            self.api_code = self.json["apiCode"]
            self.api_message = self.json["apiMsg"]
