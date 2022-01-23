from .callback_type import CallbackType
from ..api.z_headers_composer import ZHeadersComposer
from ..utils.objectification import *
from websocket import WebSocket
from threading import Thread
from asyncio import run
from types import FunctionType
from ujson import loads
from ujson import dumps

types = {
    1: "on_message",
    2: "on_server_ack",
    11: "on_conflict",
    13: "on_push"
}


class ZWebsocketListener(Thread, WebSocket):
    callbacks: list[CallbackType] = []

    def __init__(self, handshake_headers_composer: ZHeadersComposer) -> None:
        Thread.__init__(self=self, target=self.launch)
        WebSocket.__init__(self=self)
        self.composer = handshake_headers_composer
        self.uri = "wss://ws.projz.com"

    def forward(self, notification_type: int, json: dict) -> None:
        for callback in self.__class__.callbacks:
            if callback.notification_type == types[notification_type]:
                if types[notification_type] == "on_message":
                    if not json.get("smallNote") and not json.get("userList"):
                        run(callback.handler(message(json["msg"])))

    def launch(self) -> None:
        self.connect(self.uri + "/v1/chat/ws", header=self.composer.compose("/v1/chat/ws"))
        while True:
            try:
                received = self.recv()
            except Exception as e:
                print(e)
                break
            if len(received) == 0:
                self.send("")
                continue
            json = loads(received)
            self.forward(json["t"], json)

    async def send_json(self, entity: dict, disconnecting: bool = False) -> None:
        try:
            self.send(dumps(entity))
            if disconnecting:
                self.close()
        except (RuntimeError, AssertionError):
            self.send(entity)

    @classmethod
    def create(cls, composer: ZHeadersComposer):
        instance = cls(composer)
        instance.start()
        return instance

    @classmethod
    def add(cls, handler: FunctionType, notification_type: str, **kwargs) -> None:
        cls.callbacks.append(CallbackType(handler, notification_type, **kwargs))

    @classmethod
    async def send_and_disconnect(cls, composer: ZHeadersComposer, entity: dict):
        instance = cls.create(composer)
        await instance.send_json(entity, True)
