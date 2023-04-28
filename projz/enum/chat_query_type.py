from enum import Enum


class ChatQueryType(Enum):
    PRIVATE = "private"
    INVITE = "invite"
    AT_MENTION = "atMention"
    MANAGED = "managed"
    PINNED = "pinned"
