from dataclasses import dataclass
from .resource import Resource


@dataclass
class Media:
    media_id: int
    base_url: str
    resource_list: list[Resource]
    raw_json: dict
