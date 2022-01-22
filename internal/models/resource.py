from dataclasses import dataclass


@dataclass
class Resource:
    width: int
    height: int
    url: str
    is_thumbnail: bool
