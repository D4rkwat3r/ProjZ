from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from datetime import datetime
from typing import Optional
from .currency import Currency
from .gift_box import GiftBox
from .user import User
from .parse import extensions_field
from .parse import time_field
from .parse import wallet_amount_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TransferOrder:
    order_id: Optional[int] = None
    order_type: Optional[int] = None
    currency_type: Optional[int] = None
    order_status: Optional[int] = None
    from_uid: Optional[int] = None
    to_uid: Optional[int] = None
    duration: Optional[int] = None
    from_user: Optional[User] = None
    to_user: Optional[User] = None
    currency: Optional[Currency] = None
    gift_box: Optional[GiftBox] = None
    amount: Optional[int] = wallet_amount_field()
    min_claimed_time: Optional[datetime] = time_field()
    created_time: Optional[datetime] = time_field()
    expired_time: Optional[datetime] = time_field()
    extensions: dict = extensions_field()
