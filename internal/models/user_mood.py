from dataclasses import dataclass


@dataclass
class UserMood:
    type: int
    is_online: bool
