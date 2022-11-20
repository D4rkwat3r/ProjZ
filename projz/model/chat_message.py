from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .parse import extensions_field
from .user import User
from .media import Media
from .rich_format import RichFormat
from .poll import Poll
from .dice import Dice


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ChatMessage:
    created_time: Optional[datetime] = time_field()
    thread_id: Optional[int] = None
    message_id: Optional[int] = None
    uid: Optional[int] = None
    type: Optional[int] = None
    seq_id: Optional[int] = None
    content: Optional[str] = None
    author: Optional[User] = None
    media: Optional[Media] = None
    poll: Optional[Poll] = None
    dice: Optional[Dice] = None
    rich_format: Optional[RichFormat] = None
    extensions: dict = extensions_field()
