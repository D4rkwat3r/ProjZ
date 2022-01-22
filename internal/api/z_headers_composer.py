from typing import Union
from typing import Optional
from uuid import uuid4
from time import time
from ujson import dumps
from httpx import Client


class ZHeadersComposer:
    def __init__(self) -> None:
        self.sid = ""
        self._headers_template = {
            "rawDeviceId": self._device_id(),
            "appType": "MainApp",
            "appVersion": "1.23.1",
            "osType": "2",
            "deviceType": "1",
            "Accept-Language": "en-US",
            "countryCode": "EN",
            "User-Agent": "com.projz.z.android/1.23.1-12478 (Linux; U; Android 7.1.2; SM-N975F; Build/samsung-user 7.1.22)",
            "timeZone": "480",
            "carrierCountryCodes": "en",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "api.projz.com",
            "Connection": "Keep-Alive"
        }
        self._signables = [
            "rawDeviceId",
            "rawDeviceIdTwo",
            "appType",
            "appVersion",
            "osType",
            "deviceType",
            "sId",
            "countryCode",
            "reqTime",
            "User-Agent",
            "contentRegion",
            "nonce",
            "carrierCountryCodes"
        ]

    def compose(self,
                path: str,
                body: Union[str, bytes, dict, None] = None,
                content_type: str = None
                ) -> dict[str, str]:
        headers = self._headers_template.copy()
        headers["nonce"] = str(uuid4())
        headers["reqTime"] = str(int(time() * 1000))
        headers["sId"] = self.sid
        if content_type:
            headers["Content-Type"] = content_type
        final_body = None
        if isinstance(body, str):
            final_body = body.encode("utf-8")
        elif isinstance(body, bytes):
            final_body = body
        elif isinstance(body, dict):
            final_body = dumps(body)
        headers["HJTRFS"] = self._sign_request(
            path,
            headers,
            final_body
        )
        return headers

    def _sign_request(self, path: str, headers: dict, body: Optional[bytes] = None) -> str:
        return Client().post(
            "http://deepthreads.ru:24358/z/reqsig", data={
                "path": path,
                "headers": headers,
                "body": body.decode("utf-8")
            }
        ).json()["signature"]

    def _device_id(self):
        return Client().get("http://deepthreads.ru:24358/z/device").json()["device"]

    def _set_authorization_cookie(self, sId: str):
        self.sid = sId
