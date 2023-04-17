from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses_json import config
from datetime import datetime
from typing import Optional
from .user import User
from .parse import extensions_field
from .parse import time_field
from .parse import wallet_amount_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GiftBox:
    box_id: Optional[int] = None
    uid: Optional[int] = None
    to_object_id: Optional[int] = None
    to_object_type: Optional[int] = None
    currency_type: Optional[int] = None
    max_claimed_count: Optional[int] = None
    distribute_mode: Optional[int] = None
    accepted: Optional[bool] = field(metadata=config(field_name="giftBoxStatus", decoder=lambda x: x != 1), default_factory=bool)
    title: Optional[str] = None
    user: Optional[User] = None
    claimed_amount: Optional[int] = wallet_amount_field()
    expired_time: Optional[datetime] = time_field()
    created_time: Optional[datetime] = time_field()
    amount: Optional[int] = wallet_amount_field()
    extensions: dict = extensions_field()

