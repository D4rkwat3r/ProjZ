from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses_json import config
from dataclasses import field
from typing import Optional
from .currency import Currency


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserTask:
    type: Optional[int] = None
    currency: Optional[Currency] = None
    gift_box_id: Optional[int] = None
    gift_box_status: Optional[int] = field(default_factory=int)
    completed: Optional[bool] = field(metadata=config(field_name="status", decoder=lambda x: x != 1), default_factory=bool)
