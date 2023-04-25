from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..parse import time_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MultiInvitationCodeInfo:
    uid: Optional[int] = None
    code: Optional[str] = None
    created_time: Optional[datetime] = time_field()
    last_read_time: Optional[datetime] = time_field()
    status: Optional[int] = None
    label: Optional[str] = None
    generation: Optional[int] = None
    operator_uid: Optional[int] = None
    type: Optional[int] = None
    total_used_count: Optional[int] = None
    used_count: Optional[int] = None
