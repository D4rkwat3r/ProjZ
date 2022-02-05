from hmac import new
from hashlib import sha256
from hashlib import sha1
from base64 import b64encode
from typing import Union
from typing import Optional
from uuid import uuid4
from time import time
from ujson import dumps


class ZHeadersComposer:
    def __init__(self) -> None:
        self.sid = ""
        self._headers_template = {
            "rawDeviceId": self._device_id(),
            "appType": "MainApp",
            "appVersion": "1.23.4",
            "osType": "2",
            "deviceType": "1",
            "Accept-Language": "en-US",
            "countryCode": "EN",
            "User-Agent": "com.projz.z.android/1.23.4-12525 (Linux; U; Android 7.1.2; SM-N975F; Build/samsung-user 7.1.2 2)",
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
        signature_data = bytes()
        signature_data += path.encode("utf-8")
        for signable in self._signables:
            if header := headers.get(signable):
                signature_data += header.encode("utf-8")
        if body:
            signature_data += body
        mac = new(
            bytes.fromhex(
                "0705dd04686ef13c9228549386eb9164467fe99b284078b89ab96cb4ba6cc748"
            ),
            signature_data,
            sha256
        )
        return b64encode(bytes.fromhex("02") + mac.digest()).decode("utf-8")

    def _device_id(self):
        installation_id = str(uuid4())
        prefix = bytes.fromhex("02") + sha1(installation_id.encode("utf-8")).digest()
        return (
                prefix + sha1(
                    prefix + sha1(bytes.fromhex("c48833a8487cc749e66eb934d0ba7f2d608a")).digest()
                ).digest()
        ).hex()

    def _set_authorization_cookie(self, sId: str):
        self.sid = sId
