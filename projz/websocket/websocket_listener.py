from ..api import Requester
from ..error import ApiException
from ..enum import WSEventType
from ..util import SubscriptionHandler
from ..model import ChatMessage
from aiohttp import ClientSession
from aiohttp import ClientWebSocketResponse
from aiohttp import WSMsgType
from asyncio import create_task
from asyncio import sleep
from asyncio import get_running_loop
from typing import Optional
from ujson import loads
from ujson import dumps
from datetime import datetime


class WebsocketListener(SubscriptionHandler):
    def __init__(
        self,
        requester: Requester,
        logging: bool = False
    ):
        super().__init__()
        self.requester = requester
        self.provider = requester.provider
        self.language = requester.language
        self.country_code = requester.country_code
        self.time_zone = requester.time_zone
        self.device_id = requester.device_id
        self.connection: ClientWebSocketResponse = None
        self.task_receiver = None
        self.task_pinger = None
        self.client_session = None
        self.logging = logging
        self.outgoing = {}

    def _log(self, log_type: str, message_type: int, content_length: int):
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WS {log_time}] [{log_type}] [{message_type}] [{content_length} bytes]")

    async def connect(self):
        self.client_session = ClientSession(base_url="wss://ws.projz.com")
        self.connection = await self.client_session.ws_connect(
            "/v1/chat/ws",
            headers=self.requester.build_headers("/v1/chat/ws")
        )
        self.task_receiver = create_task(self.receive())
        self.task_pinger = create_task(self.ping())

    async def disconnect(self):
        self.task_receiver.cancel()
        self.task_pinger.cancel()
        await self.connection.close()
        self.connection = None
        await self.client_session.close()
        self.client_session = None

    async def receive(self):
        while True:
            msg = await self.connection.receive()
            if msg.type != WSMsgType.TEXT: continue
            msg_json = loads(msg.data)
            if self.logging:
                self._log("INCOMING", msg_json["t"], len(msg.data))
            if msg_json["t"] == WSEventType.MESSAGE.value:
                self.broadcast(ChatMessage.from_dict(msg_json["msg"]))
            elif msg_json["t"] == WSEventType.ACK.value:
                ack = msg_json["serverAck"]
                if ack["seqId"] not in self.outgoing: continue
                if ack["apiCode"] != 0:
                    self.outgoing[ack["seqId"]].set_exception(ApiException.get(ack))
                    continue
                self.outgoing[ack["seqId"]].set_result(ack)
                del self.outgoing[ack["seqId"]]

    async def ping(self):
        while True:
            await sleep(3)
            await self.send_request(8)

    async def send_request(
        self,
        request_type: int,
        wait_response: bool = False,
        seq_id: Optional[int] = None,
        **kwargs
    ) -> Optional[dict]:
        data = dumps(dict(t=request_type, **kwargs))
        if self.logging:
            self._log("OUTGOING", request_type, len(data))
        await self.connection.send_str(data)
        if wait_response:
            if seq_id is None: raise ValueError("Can't wait for response without seq id parameter")
            future = get_running_loop().create_future()
            self.outgoing[seq_id] = future
            return await future
        return None

