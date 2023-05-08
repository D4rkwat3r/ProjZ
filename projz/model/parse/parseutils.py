from datetime import datetime
from dateutil.parser import isoparse
from typing import Union
from typing import Optional
from dataclasses import Field
from dataclasses import field
from dataclasses_json import config


def decode_time(encoded_time: Union[int, str, None]) -> Optional[datetime]:
    if isinstance(encoded_time, int):
        try: return datetime.fromtimestamp(encoded_time)
        except OSError: return datetime.fromtimestamp(encoded_time // 1000)
    elif isinstance(encoded_time, str):
        return isoparse(encoded_time)
    else: return None


def encode_time(time: Optional[datetime]) -> Optional[int]:
    if time is None:
        return None
    return int(time.timestamp() * 1000)


def decode_wallet_amount(amount: str) -> int:
    if amount == "0": return 0
    return int(amount[:len(amount) - 18])


def time_field() -> Field:
    return field(metadata=config(decoder=decode_time, encoder=encode_time), default_factory=type(None))


def extensions_field() -> Field:
    return field(default_factory=dict)


def wallet_amount_field() -> Field:
    return field(metadata=config(decoder=decode_wallet_amount), default_factory=0)
