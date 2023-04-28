from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config
from dataclasses_json import LetterCase
from ..user import User
from ..member_title import MemberTitle


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemberTitlesInfo:
    titles: list[MemberTitle] = field(metadata=config(field_name="list"), default_factory=list)
    member_list_map: dict[str, list[User]] = field(default_factory=dict)
