from aiofiles.threadpool.binary import AsyncBufferedReader
from httpx import AsyncClient
from httpx import Request
from uuid import uuid4
from .z_headers_composer import ZHeadersComposer
from .z_api_response import ZApiResponse
from ..exceptions.objects.file_uploading_error import FileUploadingError


class ZMediaAPI(ZHeadersComposer):

    def __init__(self):
        super().__init__()

    async def upload_file(self, file: AsyncBufferedReader, target: int, duration: int) -> ZApiResponse:
        multipart = {
            "media": (
                file.name,
                await file.read(),
                "image/" + "jpeg" if file.name.split(".")[1] == "jpg" else file.name.split(".")[1]
            )
        }
        endpoint = f"/v1/media/upload?target={target}&duration={duration}"
        async with AsyncClient(http2=True) as http:
            request = Request(
                "POST",
                url="https://api.projz.com" + endpoint,
                files=multipart
            )
            request._prepare(self.compose(endpoint, request.read()))
            response = await http.send(request)
            api_response = ZApiResponse(response.text)
            if not api_response.is_request_succeed:
                raise FileUploadingError(code=api_response.api_code, message=api_response.api_message)
            return api_response
