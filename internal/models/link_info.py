from dataclasses import dataclass


@dataclass
class LinkInfo:
    path: str
    object_id: int
    object_type: int
    share_link: str
