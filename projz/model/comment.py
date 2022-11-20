from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .user import User
from .media import Media


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Comment:
    created_time: Optional[datetime] = time_field()
    comment_id: Optional[int] = None
    parent_type: Optional[int] = None
    parent_id: Optional[int] = None
    uid: Optional[int] = None
    status: Optional[int] = None
    content: Optional[str] = None
    comment_type: Optional[int] = None
    media_list: Optional[list[Media]] = None
    votes_count: Optional[int] = None
    author: Optional[User] = None
