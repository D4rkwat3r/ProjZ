from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .blog import Blog
from .chat import Chat


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BlockedItemWrapper:
    id: Optional[int] = None
    object_id: Optional[int] = None
    object_type: Optional[int] = None
    chat: Optional[Chat] = None
    blog: Optional[Blog] = None
    created_time: Optional[datetime] = time_field()

