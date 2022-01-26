from .custom_executor import CustomExecutor
from threading import Thread
from websocket import WebSocket
from websocket import WebSocketConnectionClosedException
from types import FunctionType
from asyncio import AbstractEventLoop
from asyncio import run
from asyncio import get_event_loop
from threading import Timer
from ssl import CERT_NONE
from ssl import SSLZeroReturnError
from ssl import SSLEOFError
from ssl import SSLError


class BaseWebsocketListener(Thread, WebSocket):
    def __init__(self) -> None:
        Thread.__init__(self=self, target=run, args=(self.launch(),))
        WebSocket.__init__(self=self, sslopt={"check_hostname": False, "cert_reqs": CERT_NONE})
        self._uri = None
        self._handshake_headers = {}
        self._ping_message = None
        self._ping_interval = None
        self._on_message = lambda message: ...
        self._on_disconnect = lambda: ...
        self._event_loop = AbstractEventLoop()

    async def launch(self) -> None:
        get_event_loop().set_default_executor(CustomExecutor())
        self.connect(self._uri, header=self._handshake_headers)
        await self.listen()

    def send(self, *args, **kwargs):
        while True:
            try:
                super().send(*args, **kwargs)
                break
            except (SSLZeroReturnError, SSLEOFError, SSLError):
                continue

    def ping_cycle(self):
        self.send(self._ping_message)
        Timer(float(self._ping_interval), self.ping_cycle).start()

    async def listen(self) -> None:
        self.ping_cycle()
        try:
            message = self.recv()
            await self._on_message(message)
            await self.listen()
        except WebSocketConnectionClosedException:
            self._on_disconnect()

    class Builder:
        def __init__(self) -> None:
            self._instance = BaseWebsocketListener()

        def set_uri(self, uri: str):
            self._instance._uri = uri
            return self

        def set_handshake_headers(self, headers: dict):
            self._instance._handshake_headers = headers
            return self

        def set_on_message(self, handler: FunctionType):
            self._instance._on_message = handler
            return self

        def set_on_disconnect(self, handler: FunctionType):
            self._instance._on_disconnect = handler
            return self

        def set_event_loop(self, loop: AbstractEventLoop):
            self._instance._event_loop = loop
            return self

        def set_ping_message(self, ping_message: str):
            self._instance._ping_message = ping_message
            return self

        def set_ping_interval(self, ping_interval: int):
            self._instance._ping_interval = ping_interval
            return self

        def build(self):
            return self._instance
