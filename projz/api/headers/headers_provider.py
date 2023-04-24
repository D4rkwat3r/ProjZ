from .abc_headers_provider import ABCHeadersProvider
from time import time


class HeadersProvider(ABCHeadersProvider):
    def __init__(self):
        self.sid = ""

    def get_persistent_headers(self) -> dict:
        return {
            "appType": "MainApp", "appVersion": "2.27.1",
            "osType": "2", "deviceType": "1", "flavor": "google",
            "User-Agent": "com.projz.z.android/2.27.1-25104 (Linux; U; Android 7.1.2; ASUS_Z01QD; Build/Asus-user 7.1.2 2017)"
        }

    def get_request_info_headers(self, device_id: str, nonce: str, language: str, country_code: str, time_zone: int) -> dict:
        headers = {
            "rawDeviceId": device_id,
            "nonce": nonce,
            "Accept-Language": language,
            "countryCode": country_code.upper(),
            "carrierCountryCodes": country_code,
            "timeZone": str(time_zone),
            "reqTime": str(int(time() * 1000))
        }
        if self.sid is not None: headers["sId"] = self.sid
        return headers

    def get_signable_header_keys(self) -> list[str]: return [
        "rawDeviceId", "rawDeviceIdTwo", "rawDeviceIdThree",
        "appType", "appVersion", "osType",
        "deviceType", "sId", "countryCode",
        "reqTime", "User-Agent", "contentRegion",
        "nonce", "carrierCountryCodes"
    ]

    def get_sid(self) -> str: return self.sid

    def set_sid(self, sid: str) -> None: self.sid = sid

    def remove_sid(self) -> None: self.sid = ""

    async def generate_request_signature(self, path: str, headers: dict, body: bytes) -> str:
        raise NotImplementedError

    async def generate_device_id(self, installation_id: str):
        raise NotImplementedError

    async def generate_device_id_three(
        self,
        organization: str,
        platform: str,
        version: str,
        model: str,
        app_id: str
    ) -> str:
        raise NotImplementedError
