from .callback_type import CallbackType
from ..api.z_headers_composer import ZHeadersComposer
from ..utils.objectification import *
from .base_websockets_listener import BaseWebsocketListener
from asyncio import sleep
from asyncio import ensure_future
from types import FunctionType
from ujson import loads
from ujson import dumps

types = {
    1: "on_message",
    2: "on_server_ack",
    11: "on_conflict",
    13: "on_push"
}


class ZWebsocketListener:
    callbacks: list[CallbackType] = []

    def __init__(self, handshake_headers_composer: ZHeadersComposer) -> None:
        self.composer = handshake_headers_composer
        self.ws = BaseWebsocketListener.Builder() \
            .set_uri("wss://ws.projz.com/v1/chat/ws") \
            .set_handshake_headers(self.composer.compose("/v1/chat/ws")) \
            .set_on_message(self.forward) \
            .set_on_error(self.restart) \
            .build()
        self.ws.start()

    def restart(self):
        self.ws.start()

    async def forward(self, entity: str) -> None:
        json = loads(entity)
        notification_type = json["t"]
        for callback in self.__class__.callbacks:
            if callback.notification_type == types[notification_type]:
                if types[notification_type] == "on_message":
                    if not json.get("smallNote") and not json.get("userList"):
                        ensure_future(callback.handler(message(json["msg"])))
                        await sleep(3)

    async def send_json(self, entity: dict, disconnecting: bool = False) -> None:
        try:
            self.ws.send(dumps(entity))
            if disconnecting:
                self.ws.close()
        except (RuntimeError, AssertionError):
            self.ws.send(entity)

    @classmethod
    def add(cls, handler: FunctionType, notification_type: str, **kwargs) -> None:
        cls.callbacks.append(CallbackType(handler, notification_type, **kwargs))

    @classmethod
    async def send_and_disconnect(cls, composer: ZHeadersComposer, entity: dict):
        instance = cls(composer)
        await instance.send_json(entity, True)
