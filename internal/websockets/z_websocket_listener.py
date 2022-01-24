from .callback_type import CallbackType
from ..api.z_headers_composer import ZHeadersComposer
from ..utils.objectification import *
from .base_websockets_listener import BaseWebsocketListener
from ..exceptions.other.message_sending_error import MessageSendingError
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
        self.outgoing_entity_list = []
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
        for callback in self.__class__.callbacks:
            if callback.notification_type == types[notification_type]:
                msg = json["msg"]
                if types[notification_type] == "on_message":
                    if msg["type"] == 1:
                        if msg["uid"] != self.client.get_current_session().uid:
                            await callback.handler(message(msg))

    async def send_json(self, entity: dict, seqId: Optional[int] = None, disconnecting: bool = False) -> dict:
        try:
            self.ws.send(dumps(entity))
            while True:
                incoming = loads(self.ws.recv())
                if types[incoming["t"]] == "on_server_ack" and incoming["serverAck"]["seqId"] == seqId:
                    if disconnecting:
                        self.ws.close()
                    if incoming["serverAck"]["apiCode"] != 0:
                        raise MessageSendingError(
                            code=incoming["serverAck"]["apiCode"],
                            message=incoming["serverAck"]["apiMsg"]
                        )
                    return incoming["serverAck"]
                else:
                    continue
        except (RuntimeError, AssertionError) as e:
            self.ws.send(entity)

    @classmethod
    def add(cls, handler: FunctionType, notification_type: str, **kwargs) -> None:
        cls.callbacks.append(CallbackType(handler, notification_type, **kwargs))

    @classmethod
    async def send_and_disconnect(cls, composer: ZHeadersComposer, entity: dict, seqId: Optional[int] = None) -> dict:
        instance = cls(composer)
        return await instance.send_json(entity, seqId, disconnecting=True)
