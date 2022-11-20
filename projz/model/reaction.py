from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .sticker import Sticker


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Reaction:
    created_time: Optional[datetime] = time_field()
    object_id: Optional[int] = None
    sticker_id: Optional[int] = None
    object_type: Optional[int] = None
    count: Optional[int] = None
    sticker: Optional[Sticker] = None
