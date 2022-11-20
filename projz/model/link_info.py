from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LinkInfo:
    path: Optional[str] = None
    object_id: Optional[int] = None
    object_type: Optional[int] = None
    share_link: Optional[str] = None
    parent_type: Optional[int] = None
