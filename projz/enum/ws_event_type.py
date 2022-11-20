from enum import Enum


class WSEventType(Enum):
    MESSAGE = 1
    ACK = 2
    PUSH = 13
