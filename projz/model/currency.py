from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .media import Media
from .parse import wallet_amount_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Currency:
    currency_type: Optional[int] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    icon: Optional[Media] = None
    amount: Optional[int] = wallet_amount_field()
    decimals: Optional[int] = field(default_factory=lambda: 18)
