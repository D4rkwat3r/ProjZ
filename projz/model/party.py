from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from .user import User
from .chat import Chat
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Party:
    admin_user: Optional[User] = None
    chat_thread_list: list[Chat] = field(default_factory=list)
