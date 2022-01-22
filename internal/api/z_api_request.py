from .z_headers_composer import ZHeadersComposer
from ..exceptions.other.request_initializing_error import RequestInitializingError
from ..exceptions.other.unauthorized import Unauthorized
from .z_api_response import ZApiResponse
from ..exceptions.finder import get_exception
from typing import Optional
from httpx import AsyncClient
from httpx import Timeout
from ujson import dumps


class ZApiRequest:
    def __init__(
            self,
            method: str,
            endpoint: str,
            body: Optional[dict] = None,
            extra_headers: Optional[dict] = None,
            composer: ZHeadersComposer = ZHeadersComposer()
    ) -> None:
        self.method = method
        self.endpoint = endpoint
        self.body = dumps(body) if body is not None else None
        self.timeout = Timeout(60.0, connect=60.0)
        if method.upper() != method:
            raise RequestInitializingError("Name of HTTP method must be in uppercase")
        if method not in ["GET", "HEAD", "DELETE"] and not self.body:
            self.body = ""
        self.request_headers = composer.compose(endpoint, self.body)
        if extra_headers:
            for extra_key, extra_value in zip(extra_headers.keys(), extra_headers.values()):
                self.request_headers[extra_key] = extra_value

    async def send(self) -> ZApiResponse:
        if "/auth/" not in self.endpoint and "sId" not in self.request_headers:
            raise Unauthorized("You must be logged in to send this request")
        async with AsyncClient(base_url="https://api.projz.com", timeout=self.timeout, http2=True) as http:
            response = await http.request(
                self.method,
                url=self.endpoint,
                headers=self.request_headers,
                data=self.body
            )
            api_response = ZApiResponse(response.text)
            if not api_response.is_request_succeed:
                raise get_exception(api_response.json)
            return api_response
