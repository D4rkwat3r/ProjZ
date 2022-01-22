from dataclasses import dataclass


@dataclass
class UserProfileExtensions:
    open_days_in_row: int
    max_open_days_in_row: int
    last_open_date: str
    is_app_rated: bool
    sticker_claimed_mask: int
    social_invite_count: int
    chat_bubble_color: str
    preview_blog_ids: list[int]
    is_gender_modified: bool
    is_ignoring_review_mode: bool
