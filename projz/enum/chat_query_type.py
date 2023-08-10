from enum import Enum


class EChatQueryType(Enum):
    PRIVATE = "private"
    INVITE = "invite"
    AT_MENTION = "atMention"
    MANAGED = "managed"
    PINNED = "pinned"
