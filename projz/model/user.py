from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses_json import config
from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from datetime import datetime
from .member_title import MemberTitle
from .media import Media
from .rich_format import RichFormat
from .sticker import Sticker
from .parse import time_field
from .parse import extensions_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class User:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class ProfileFrame:
        resource: Optional[Media] = field(metadata=config(field_name="res"))
        created_time: Optional[datetime] = time_field()
        profile_frame_id: Optional[int] = None
        name: Optional[str] = None
        profile_frame_parent_id: Optional[int] = None
        profile_frame_parent_type: Optional[int] = None

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class UserMood:
        type: Optional[int] = None
        sticker_id: Optional[int] = None
        online_status: Optional[int] = None
        sticker: Optional[Sticker] = None

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class UserVisitorInfo:
        user_profile_visit_mode: Optional[int] = None

    created_time: Optional[datetime] = time_field()
    last_active_time: Optional[datetime] = time_field()
    uid: Optional[str] = None
    nickname: Optional[str] = None
    social_id: Optional[str] = None
    social_id_modified: Optional[str] = None
    bio: Optional[str] = None
    rich_format: Optional[RichFormat] = None
    gender: Optional[int] = None
    status: Optional[int] = None
    icon: Optional[Media] = None
    name_card_background: Optional[Media] = None
    background: Optional[Media] = None
    preview_media_list: Optional[list[Media]] = None
    profile_frame: Optional[ProfileFrame] = None
    media_list: Optional[list[Media]] = None
    chat_invitation_status: Optional[int] = None
    public_chat_invitation_status: Optional[int] = None
    private_chat_invitation_status: Optional[int] = None
    circle_invitation_status: Optional[int] = None
    online_status: Optional[int] = None
    content_region_name: Optional[str] = None
    user_mood: Optional[UserMood] = None
    content_region: Optional[int] = None
    shows_school: Optional[int] = None
    shows_location: Optional[int] = None
    name_card_enabled: Optional[int] = None
    match_enabled: Optional[int] = None
    tagline: Optional[str] = None
    zodiac_type: Optional[int] = None
    language: Optional[str] = None
    country_code: Optional[str] = None
    push_enabled: Optional[int] = None
    shows_joined_circles: Optional[int] = None
    birthday: Optional[str] = None
    comments_count: Optional[int] = None
    comment_permission_type: Optional[int] = None
    third_party_uid: Optional[str] = None
    user_visitor_info: Optional[UserVisitorInfo] = None
    wallet_activated: Optional[int] = None
    fans_count: Optional[int] = None
    friends_count: Optional[int] = None
    blogs_count: Optional[int] = None
    circle_member_title_list: list[MemberTitle] = field(default_factory=list)
    circle_joined_time: Optional[datetime] = time_field()
    circle_role: Optional[int] = None
    joined_status: Optional[int] = None
    extensions: dict = extensions_field()
