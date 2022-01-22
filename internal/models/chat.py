from dataclasses import dataclass
from .media import Media
from .user_profile import UserProfile
from .message import Message


@dataclass
class Chat:
    thread_id: int
    status: int
    type: int
    host_uid: int
    title: str
    icon: Media
    content: str
    latest_message_id: int
    members_count: int
    all_members_count: int
    background: Media
    content_region: int
    # category
    welcome_message: str
    created_time: int
    # updated time
    members_summary: list[UserProfile]
    language: str
    visibility: int
    roles_count: int
    # current member info
    latest_message: Message
    host: UserProfile
    qi_voted_count: int
    using_role_count: int
    talking_member_count: int
    roleplayer_count: int
