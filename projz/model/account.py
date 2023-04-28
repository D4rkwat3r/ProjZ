from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .parse import time_field


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Account:
    uid: Optional[int] = None
    status: Optional[int] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    has_profile: Optional[int] = None
    has_password: Optional[int] = None
    current_device_id: Optional[str] = None
    current_device_id2: Optional[str] = None
    current_device_id3: Optional[str] = None
    registered_device_id: Optional[str] = None
    registered_device_id2: Optional[str] = None
    registered_device_id3: Optional[str] = None
    registered_ipv4: Optional[str] = None
    last_login_ipv4: Optional[str] = None
    created_time: Optional[datetime] = time_field()
