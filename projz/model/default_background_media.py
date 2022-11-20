from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .media import Media


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DefaultBackgroundMedia:
    created_time: Optional[datetime] = time_field()
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    activityTitle: Optional[str] = None
    uid: Optional[int] = None
    pos: Optional[int] = None
    media: Optional[Media] = None
    from_field: Optional[int] = None
