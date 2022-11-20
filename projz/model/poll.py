from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .parse import extensions_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Poll:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class PollItem:
        created_time: Optional[datetime] = time_field()
        poll_id: Optional[int] = None
        poll_item_id: Optional[int] = None
        content: Optional[str] = None
    created_time: Optional[datetime] = time_field()
    poll_id: Optional[int] = None
    uid: Optional[int] = None
    title: Optional[str] = None
    poll_item_list: Optional[list[PollItem]] = None
    extensions: dict = extensions_field()
