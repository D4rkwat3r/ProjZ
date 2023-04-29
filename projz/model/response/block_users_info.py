from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BlockUsersInfo:
    blocked_by_me_list: list[int] = field(default_factory=list)
    block_me_list: list[int] = field(default_factory=list)
