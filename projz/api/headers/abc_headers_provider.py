from abc import ABC
from typing import Optional


class ABCHeadersProvider(ABC):
    def get_persistent_headers(self) -> dict: ...

    def get_request_info_headers(self,
                                 device_id: str,
                                 nonce: str,
                                 language: str,
                                 country_code: str,
                                 time_zone: int) -> dict: ...

    def get_signable_header_keys(self) -> list[str]: ...

    def get_sid(self) -> str: ...

    def set_sid(self, sid: str) -> None: ...

    def remove_sid(self) -> None: ...

    async def generate_request_signature(self, path: dict, headers: dict, body: bytes) -> str: ...

    async def generate_device_id(self, installation_id: str) -> str: ...

    async def generate_device_id_three(
        self,
        organization: str,
        platform: str,
        version: str,
        model: str,
        app_id: str
    ) -> str: ...
