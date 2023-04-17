from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from datetime import datetime
from typing import Optional
from .currency import Currency
from .parse import extensions_field
from .parse import time_field
from .parse import wallet_amount_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Wallet:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class WalletAccount:
        @dataclass_json(letter_case=LetterCase.CAMEL)
        @dataclass
        class WalletCurrencyListItem:
            account_id: Optional[int] = None
            currency_type: Optional[int] = None
            balance: Optional[Currency] = None
            available_currency: Optional[Currency] = None
            balance_value: Optional[int] = wallet_amount_field()
            created_time: Optional[datetime] = time_field()
        account_id: Optional[int] = None
        account_type: Optional[int] = None
        status: Optional[int] = None
        owner_id: Optional[int] = None
        owner_type: Optional[int] = None
        created_time: Optional[datetime] = time_field()
        currency_list: list[WalletCurrencyListItem] = field(default_factory=list)

    uid: Optional[int] = None
    activate_status: Optional[int] = None
    status: Optional[int] = None
    payment_password_version: Optional[int] = None
    regular_account: Optional[WalletAccount] = None
    last_read_transfer_order_id: Optional[int] = None
    created_time: Optional[datetime] = time_field()
    wallet_extensions: dict = extensions_field()
