from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .parse import extensions_field
from .media import Media
from .user import User
from .category import Category


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Circle:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class CircleBackground:
        background_image: Optional[Media] = None
    created_time: Optional[datetime] = time_field()
    updated_time: Optional[datetime] = time_field()
    circle_id: Optional[int] = None
    category_id: Optional[int] = None
    concept_id: Optional[int] = None
    category: Optional[Category] = None
    social_id: Optional[str] = None
    social_id_modified: Optional[int] = None
    status: Optional[int] = None
    verified_status: Optional[int] = None
    name: Optional[str] = None
    tagline: Optional[str] = None
    language: Optional[str] = None
    content_region: Optional[int] = None
    members_count: Optional[int] = None
    daily_active_user: Optional[int] = None
    daily_new_post_count: Optional[int] = None
    privacy: Optional[int] = None
    join_permission: Optional[int] = None
    visibility: Optional[int] = None
    discoverability: Optional[int] = None
    icon: Optional[Media] = None
    cover: Optional[Media] = None
    circle_icon: Optional[Media] = None
    circle_background: Optional[CircleBackground] = None
    theme_color: Optional[str] = None
    joined_status: Optional[int] = None
    uid: Optional[int] = None
    author: Optional[User] = None
    background: Optional[Media] = None
    admin_id_list: Optional[list[int]] = None
    co_admin_id_list: Optional[list[int]] = None
    root_folder_id: Optional[int] = None
    description: Optional[str] = None
    # rich format
    # home tab background
    # home layout
    # menu
    # current member info
    extensions: dict = extensions_field()
