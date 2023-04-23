from .headers_provider import HeadersProvider
from aiohttp import ClientSession
from marshal import dumps
from marshal import loads
from typing import Any


class RPCHeadersProvider(HeadersProvider):
    def __init__(self):
        super().__init__()
        self.rpc_base = "http://deepthreads.ru/rpc?func={}".format

    async def _rpc(self, func: str, *args, **kwargs) -> Any:
        async with ClientSession() as session:
            response = loads(await (await session.post(self.rpc_base(func), data=dumps((args, kwargs)))).read())
        if isinstance(response, tuple) and response[0] == "e":
            raise Exception(f"{response[1]}(\"{response[2]}\")")
        return response

    async def generate_request_signature(self, path: str, headers: dict, body: bytes) -> str:
        return await self._rpc("projz_generate_signature", path, headers, body)

    async def generate_device_id(self, installation_id: str) -> str:
        return await self._rpc("projz_generate_device_id", installation_id)
