from .headers_provider import HeadersProvider
from ..control import RPC


class RPCHeadersProvider(HeadersProvider):
    def __init__(self):
        super().__init__()

    async def generate_request_signature(self, path: str, headers: dict, body: bytes) -> str:
        return await RPC.generate_request_signature(path, headers, body)

    async def generate_device_id(self, installation_id: str) -> str:
        return await RPC.generate_device_id(installation_id)

    async def generate_device_id_three(
        self,
        organization: str,
        platform: str,
        version: str,
        model: str,
        app_id: str
    ) -> str:
        return await RPC.generate_smid(organization, platform, version, model, app_id)
