from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .parse import extensions_field
from .media import Media
from .rich_format import RichFormat
from .user import User
from .circle import Circle
from .reaction import Reaction


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Blog:
    created_time: Optional[datetime] = time_field()
    edited_time: Optional[datetime] = time_field()
    updated_time: Optional[datetime] = time_field()
    blog_id: Optional[int] = None
    circle_id_list: Optional[list[int]] = None
    status: Optional[int] = None
    type: Optional[int] = None
    uid: Optional[int] = None
    content: Optional[str] = None
    rich_format: Optional[RichFormat] = None
    cover: Optional[Media] = None
    media_list: Optional[list[Media]] = None
    votes_count: Optional[int] = None
    comments_count: Optional[int] = None
    content_region: Optional[int] = None
    language: Optional[str] = None
    visibility: Optional[int] = None
    is_user_pinned: bool = False
    author: Optional[User] = False
    circle_list: Optional[list[Circle]] = None
    reaction_count_list: Optional[list[Reaction]] = None
    extensions: dict = extensions_field()
