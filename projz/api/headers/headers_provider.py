from .abc_headers_provider import ABCHeadersProvider
from ujson import load
from ujson import dumps
from hashlib import sha1
from hmac import HMAC
from hashlib import sha256
from base64 import b64encode
from base64 import urlsafe_b64encode
from typing import Optional
from time import time
from os import urandom


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

    def generate_request_signature(self, path: str, headers: dict, body: bytes) -> str:
        mac = HMAC(key=bytes.fromhex("ebefcf164b887da7f924c948e1fc3e40faf230eb7d491c1de1150134b8517189"),
                   msg=path.encode("utf-8"),
                   digestmod=sha256)
        for header in [headers[signable] for signable in self.get_signable_header_keys() if signable in headers]:
            mac.update(header.encode("utf-8"))
        if body: mac.update(body)
        return b64encode(bytes.fromhex("01") + mac.digest()).decode("utf-8")

    def generate_device_id(self, installation_id: str):
        prefix = bytes.fromhex("01") + sha1(installation_id.encode("utf-8")).digest()
        return (
            prefix + sha1(
                prefix + sha1(bytes.fromhex("dcfed9e64710da3a8458298424ff88e47375")).digest()
            ).digest()
        ).hex()

    def _jwt_hs256(self, header: dict, data: dict, key: bytes) -> str:
        header_json = dumps(dict(alg="HS256", **header))
        data_json = dumps(data)
        body_str = f"{urlsafe_b64encode(header_json.encode('utf-8')).decode('utf-8')}" \
                   f".{urlsafe_b64encode(data_json.encode('utf-8')).decode('utf-8')}"
        sign = HMAC(key=key,
                    msg=body_str.encode("utf-8"),
                    digestmod=sha256).digest()
        return f"{body_str}.{urlsafe_b64encode(sign).decode('utf-8')}".replace("=", "")

    def generate_device_id_three(self, data: Optional[dict] = None) -> str:
        return "D" + self._jwt_hs256({
            "organization": "BU0gJ0gB5TFcCfN329Vx",
            "os": "android",
            "appId": "default",
            "encode": 1,
            "data": self._jwt_hs256(data or {
                "a1": "exception",
                "a6": "android",
                "a7": "3.0.6",
                "a2": "",
                "a10": "7.1.2",
                "a13": "ASUS_Z01QD",
                "a96": "BU0gJ0gB5TFcCfN329Vx",
                "a11": "default",
                "a98": b64encode("BU0gJ0gB5TFcCfN329Vx_bzcVDxF2PO"
                                 "/ArnWpiOIWhT0WwjQ76FZ6BqAnhQpqI"
                                 "OeGJYJvV5bcTZQ0lgjRQNAcyAqhRi7Ym"
                                 "7tNesvah21ROA==".encode('utf-8')).decode("utf-8"),
                "e": "",
                "a97": "",
            }, {}, urandom(256)),
            "tn": "",
            "ep": "",
        }, {}, urandom(256))