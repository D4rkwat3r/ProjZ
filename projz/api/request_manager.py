from .headers import ABCHeadersProvider
from .util import CopyToBufferWriter
from ..error import ApiException
from ..error import BadResponse
from io import BytesIO
from aiohttp import ClientSession
from aiohttp import MultipartWriter
from typing import Optional
from typing import Union
from uuid import uuid4
from ujson import dumps
from ujson import loads
from ujson import JSONDecodeError
from dataclasses_json import DataClassJsonMixin
from urllib.parse import urlencode
from datetime import datetime
from random import randint
from struct import pack
from socket import inet_ntoa


class RequestManager:
    def __init__(
        self,
        provider: ABCHeadersProvider,
        language: str = "en-US",
        country_code: str = "us",
        time_zone: int = 180,
        logging: bool = False
    ):
        self.provider = provider
        self.language = language
        self.country_code = country_code
        self.time_zone = time_zone
        self.device_id = None
        self.logging = logging

    async def build_headers(self, endpoint: str, body: Optional[bytes] = None, extra: Optional[dict] = None) -> dict:
        if self.device_id is None:
            self.device_id = await self.provider.generate_device_id(str(uuid4()))
        headers = self.provider.get_persistent_headers()
        headers.update(self.provider.get_request_info_headers(
            self.device_id,
            str(uuid4()),
            self.language,
            self.country_code,
            self.time_zone
        ))
        headers.update(extra or {})
        headers["X-Forwarded-For"] = inet_ntoa(pack(">I", randint(1, 0xffffffff)))
        headers["HJTRFS"] = await self.provider.generate_request_signature(endpoint, headers, body or bytes())
        return headers

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        body: Optional[bytes] = None,
        content_type: Optional[str] = None,
        web: bool = True
    ) -> dict:
        if not endpoint.startswith("/"): endpoint = f"/{endpoint}"
        if params: endpoint += f"?{urlencode(params)}"
        if web: endpoint = f"/api/f{endpoint}"
        if self.logging:
            request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"[HTTP {request_time}] " +
                (f"[{method} {endpoint}]" if body is None else f"[{method} {endpoint}] [{len(body)} bytes]")
            )
        async with ClientSession(base_url="https://api.projz.com" if not web else "https://www.projz.com") as session:
            response = await session.request(
                method,
                endpoint,
                headers=await self.build_headers(
                    endpoint,
                    body,
                    {"Content-Type": content_type} if content_type is not None else None
                ) if not web else dict(),
                data=body
            )
            try: response_json = loads(await response.text())
            except (JSONDecodeError, UnicodeDecodeError): raise BadResponse("Can't read response from Project Z API")
            if "apiCode" in response_json: raise ApiException.get(response_json)
            return response_json

    async def get(self, endpoint: str, params: Optional[dict] = None, web: bool = False) -> dict:
        return await self.request("GET", endpoint, params=params or dict(), web=web)

    async def delete(self, endpoint: str, params: Optional[dict] = None, web: bool = False) -> dict:
        return await self.request("DELETE", endpoint, params=params or dict(), web=web)

    async def post(
        self,
        endpoint: str,
        body: Union[bytes, str, dict, DataClassJsonMixin, MultipartWriter],
        content_type: Optional[str],
        web: bool = False
    ) -> dict:
        content = BytesIO()
        if isinstance(body, bytes): content.write(body)
        elif isinstance(body, str): content.write(body.encode("utf-8"))
        elif isinstance(body, dict): content.write(dumps(body).encode("utf-8"))
        elif isinstance(body, DataClassJsonMixin): content.write(body.to_json().encode("utf-8"))
        elif isinstance(body, MultipartWriter): await body.write(CopyToBufferWriter(content))
        else: raise ValueError(f"Invalid request body type: \"{body.__class__.__name__}\"")
        return await self.request("POST", endpoint, body=content.getvalue(), content_type=content_type, web=web)

    async def post_json(self, endpoint: str, body: Union[dict, DataClassJsonMixin], web: bool = False) -> dict:
        return await self.post(endpoint, body=body, content_type="application/json; charset=UTF-8", web=web)

    async def post_empty(self, endpoint: str, web: bool = False):
        return await self.post(endpoint, body="", content_type=None, web=web)
