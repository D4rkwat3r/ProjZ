from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses_json import config
from dataclasses import dataclass
from dataclasses import field
from ..account import Account
from ..user import User


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthResponse:
    secret: str
    account: Account
    user_profile: User
    sid: str = field(metadata=config(field_name="sId"))
