import websockets.exceptions

from .callback_type import CallbackType
from ..api.z_headers_composer import ZHeadersComposer
from ..utils.objectification import *
from websockets import connect
from asyncio import new_event_loop
from asyncio import set_event_loop
from threading import Thread
from types import FunctionType
from ujson import loads
from ujson import dumps

types = {
    1: "on_message",
    2: "on_server_ack",
    11: "on_conflict",
    13: "on_push"
}


class ZWebsocketConnection(Thread):
    callbacks: list[CallbackType] = []

    def __init__(self, handshake_headers_composer: ZHeadersComposer):
        super().__init__(target=self.setup)
        self.composer = handshake_headers_composer
        self.uri = "wss://ws.projz.com"
        self.connection = None
        self.thread_loop = None

    async def forward(self, notification_type: int, json: dict):
        for callback in self.__class__.callbacks:
            if callback.notification_type == types[notification_type]:
                if types[notification_type] == "on_message":
                    if not json.get("smallNote") and not json.get("userList"):
                        await callback.handler(message(json["msg"]))

    async def launch_handling(self):
        self.connection = await connect(self.uri + "/v1/chat/ws", extra_headers=self.composer.compose("/v1/chat/ws"))
        while True:
            try:
                received = await self.connection.recv()
            except websockets.exceptions.ConnectionClosed:
                break
            if len(received) == 0:
                await self.connection.send("")
                continue
            try:
                json = loads(received)
            except:
                continue
            if json["t"] in types:
                await self.forward(json["t"], json)

    async def send(self, entity: dict):
        try:
            await self.connection.send(dumps(entity))
        except (RuntimeError, AssertionError):
            await self.send(entity)

    def setup(self):
        loop = new_event_loop()
        set_event_loop(loop)
        loop.run_until_complete(self.launch_handling())
        loop.run_forever()

    @classmethod
    def create(cls, composer: ZHeadersComposer):
        # The websockets library, being the only asynchronous library for working with websockets,
        # does not have built-in support for background work with callbacks,
        # asyncio.create_task or asyncio.ensure_future do not prevent scripts from terminating like as daemon threads,
        # so we have to use such a stupid stub.
        instance = cls(composer)
        instance.start()
        instance.join(0.1)
        return instance

    @classmethod
    def add(cls, handler: FunctionType, notification_type: str, **kwargs):
        cls.callbacks.append(CallbackType(handler, notification_type, **kwargs))

    @classmethod
    async def send_and_disconnect(cls, composer: ZHeadersComposer, entity: dict):

        # unstable

        instance = cls(composer)
        instance.start()
        instance.join(0.1)
        await instance.send(entity)
        await instance.connection.close_connection()
