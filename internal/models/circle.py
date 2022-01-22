from dataclasses import dataclass
from .media import Media


@dataclass
class Circle:
    circle_id: int
    category_id: int
    concept_id: str
    social_id: str
    is_social_id_modified: bool
    created_time: int
    updated_time: str
    status: int
    verified_status: int
    name: str
    tagline: str
    language: str
    content_region: str
    members_count: int
    daily_active_users: int
    daily_new_posts_count: int
    visibility: int
    icon: Media
    raw_json: dict
