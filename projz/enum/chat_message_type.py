from enum import Enum


class EChatMessageType(Enum):
    TEXT = 1
    MEDIA = 2
    AUDIO = 6
    STICKER = 7
    DICE = 44
    POLL = 45
    TYPING = 60
