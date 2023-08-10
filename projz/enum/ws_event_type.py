from enum import Enum


class EWebSocketEventType(Enum):
    MESSAGE = 1
    ACK = 2
    PUSH = 13
