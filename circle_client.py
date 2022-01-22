from .internal.models.account import Account
from .internal.models.circle import Circle
from .internal.websockets.z_websocket_connection import ZWebsocketConnection
from typing import Optional


class CircleClient:
    def __init__(self, parent, session: Account, circle: Circle, websocket: ZWebsocketConnection):
        parent.__init__()
        parent._session = session
        parent._circle = circle
        parent._websocket = websocket
        self._session = session
        self._circle = circle
        self._websocket = websocket

    def get_parent_session(self) -> Optional[Account]:
        return self._session

    def get_circle(self) -> Circle:
        return self._circle

