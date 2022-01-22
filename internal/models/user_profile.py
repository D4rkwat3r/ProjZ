from dataclasses import dataclass
from .media import Media
from .user_profile_extensions import UserProfileExtensions
from .user_mood import UserMood


@dataclass
class UserProfile:
    uid: str
    nickname: str
    social_id: str
    is_social_id_modified: bool
    gender: int
    status: int
    icon: Media
    chat_invitation_status: int
    extensions: UserProfileExtensions
    is_online: bool
    created_time: int
    content_region: int
    content_region_name: str
    user_mood: UserMood
    shows_school: bool
    last_active_time: int
    shows_location: int
    name_card_enabled: int
    match_enabled: int
    name_card_background: Media
    background: Media
    tagline: str
    zodiac_type: int
    language: str
    is_push_enabled: bool
    shows_joined_circles: int
    birthday: str
    fans_count: int
    following_count: int
    friends_count: int
    comments_count: int
    comment_permission_type: int
    third_party_uid: str
