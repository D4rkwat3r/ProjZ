from .z_headers_composer import ZHeadersComposer
from .z_api_request import ZApiRequest
from .z_api_response import ZApiResponse
from ujson import dumps
from typing import Optional
from typing import BinaryIO


class ZHttpAPI(ZHeadersComposer):
    def __init__(self):
        super().__init__()

    async def _post(self, endpoint: str, data: Optional[dict] = None) -> ZApiResponse:
        response = await ZApiRequest("POST", endpoint, data, composer=self).send()
        return response

    async def _get(self, endpoint: str) -> ZApiResponse:
        response = await ZApiRequest("GET", endpoint, composer=self).send()
        return response

    async def _delete(self, endpoint: str) -> ZApiResponse:
        response = await ZApiRequest("DELETE", endpoint, composer=self).send()
        return response

    async def _send_custom(self, request: ZApiRequest) -> ZApiResponse:
        return await request.send()
