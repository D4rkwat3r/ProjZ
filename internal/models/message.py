from dataclasses import dataclass
from .user_profile import UserProfile


@dataclass
class Message:
    thread_id: int
    message_id: int
    uid: int
    created_time: int
    type: int
    asSummary: bool
    content: str
    author: UserProfile
