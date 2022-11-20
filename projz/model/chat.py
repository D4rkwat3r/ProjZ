from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .media import Media
from .rich_format import RichFormat
from .category import Category
from .user import User
from .chat_message import ChatMessage
from .blog import Blog
from .circle import Circle


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Chat:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class EventTag:
        endTime: Optional[datetime] = time_field()
        tagId: Optional[int] = None
        tagName: Optional[str] = None
        media: Optional[Media] = None
        status: Optional[int] = None
    created_time: Optional[datetime] = time_field()
    updated_time: Optional[datetime] = time_field()
    thread_id: Optional[int] = None
    type: Optional[int] = None
    host_uid: Optional[int] = None
    co_host_uids: Optional[list[int]] = None
    title: Optional[str] = None
    icon: Optional[Media] = None
    background: Optional[Media] = None
    content: Optional[str] = None
    rich_format: Optional[RichFormat] = None
    latest_message_id: Optional[int] = None
    members_count: Optional[int] = None
    all_members_count: Optional[int] = None
    content_region: Optional[int] = None
    category_id: Optional[int] = None
    concept_id: Optional[int] = None
    category: Optional[Category] = None
    welcome_message: Optional[str] = None
    members_summary: Optional[list[User]] = None
    language: Optional[str] = None
    visibility: Optional[int] = None
    roles_count: Optional[int] = None
    # current member info
    latest_message: Optional[ChatMessage] = None
    host: Optional[User] = None
    revolving_lantern_blog: Optional[Blog] = None
    circle_id_list: Optional[list[int]] = None
    circle_list: Optional[list[Circle]] = None
    qi_voted_count: Optional[int] = None
    event_tag: Optional[EventTag] = None
    using_role_count: Optional[int] = None
    talking_member_count: Optional[int] = None
    roleplayer_count: Optional[int] = None
    # mentionedBy
    plt: Optional[int] = None
