from .callback_type import CallbackType
from ..api.z_headers_composer import ZHeadersComposer
from ..utils.objectification import *
from .base_websockets_listener import BaseWebsocketListener
from types import FunctionType
from ujson import loads
from ujson import dumps
from typing import Optional

types = {
    1: "on_message",
    2: "on_server_ack",
    11: "on_conflict",
    13: "on_push"
}


class ZWebsocketListener:
    callbacks: list[CallbackType] = []

    def __init__(self, client_instance) -> None:
        self.client = client_instance
        self.outgoing_entity = {}
        self.ws = BaseWebsocketListener.Builder() \
            .set_uri("wss://ws.projz.com/v1/chat/ws") \
            .set_handshake_headers(self.client.compose("/v1/chat/ws")) \
            .set_on_message(self.forward) \
            .set_ping_message(dumps({"t": 8})) \
            .set_ping_interval(15) \
            .build()
        self.ws.start()

    def restart(self):
        self.__init__(self.client)

    async def forward(self, entity: str) -> None:
        try:
            json = loads(entity)
        except:
            return
        notification_type = json["t"]
        if types[notification_type] == "on_server_ack":
            seq_id = json["serverAck"]["seqId"]
            if seq_id in self.outgoing_entity:
                raises = self.outgoing_entity[seq_id]["raise"]
                self.outgoing_entity.pop(seq_id)
                if json["serverAck"]["apiCode"] != 0:
                    raise raises(
                        code=json["serverAck"]["apiCode"],
                        message=json["serverAck"]["apiMsg"]
                    )
                return
        for callback in self.__class__.callbacks:
            if callback.notification_type == types[notification_type]:
                msg = json["msg"]
                if types[notification_type] == "on_message":
                    if msg["type"] == 1:
                        if msg["uid"] != self.client.get_current_session().uid:
                            await callback.handler(message(msg))

    async def send_json(self, entity: dict, raises, seqId: Optional[int] = None, disconnecting: bool = False) -> dict:
        try:
            self.ws.send(dumps(entity))
            self.outgoing_entity[seqId] = {"raise": raises}
        except (RuntimeError, AssertionError) as e:
            return await self.send_json(entity, raises, seqId, disconnecting)

    @classmethod
    def add(cls, handler: FunctionType, notification_type: str, **kwargs) -> None:
        cls.callbacks.append(CallbackType(handler, notification_type, **kwargs))

    @classmethod
    async def send_and_disconnect(cls, composer: ZHeadersComposer, entity: dict, raises, seqId: Optional[int] = None) -> dict:
        instance = cls(composer)
        return await instance.send_json(entity, raises, seqId, disconnecting=True)
