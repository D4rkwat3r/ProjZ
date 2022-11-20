from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class QiVoteInfo:
    created_time: Optional[datetime] = time_field()
    last_vote_time: Optional[datetime] = time_field()
    object_type: Optional[int] = None
    uid: Optional[int] = None
    voted_date: Optional[int] = None
    voted_count: Optional[int] = None
    total_voted_count: Optional[int] = None
