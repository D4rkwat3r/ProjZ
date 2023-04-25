from pickle import loads
from pickle import dumps
from pickle import UnpicklingError
from aiohttp import ClientSession
from aiohttp import ClientError
from typing import Any


class RPC:

    RPC_SERVER = "http://deepthreads.ru"
    PICKLE_PROTOCOL = 4

    @classmethod
    async def _rpc(cls, func: str, *args, **kwargs) -> Any:
        async with ClientSession(base_url=cls.RPC_SERVER) as session:
            data = dumps((args, kwargs), protocol=cls.PICKLE_PROTOCOL)
            try:
                response = loads(
                    await (await session.post(f"/rpc?func={func}&v={cls.PICKLE_PROTOCOL}", data=data)).read()
                )
                if isinstance(response, tuple) and response[0] == "e":
                    raise Exception(f"RPC error ({response[1]}). {response[2]}")
            except UnpicklingError:
                raise ValueError(f"Cannot unpickle response from the RPC server.")
            except ClientError:
                raise ConnectionError(f"Cannot send request to the RPC server.")
        return response

    @classmethod
    async def generate_request_signature(cls, path: str, headers: dict, body: bytes) -> str:
        return await cls._rpc("projz_generate_request_signature", path, headers, body)

    @classmethod
    async def generate_device_id(cls, installation_id: str) -> str:
        return await cls._rpc("projz_generate_device_id", installation_id)

    @classmethod
    async def generate_smid(cls, organization: str, platform: str, version: str, model: str, app_id: str):
        return await cls._rpc("projz_generate_smid", organization, platform, version, model, app_id)

    @classmethod
    async def generate_wallet_recovery_data(cls, strength: int, language: str) -> tuple[str, str]:
        return await cls._rpc("projz_generate_wallet_recovery_data", strength, language)
