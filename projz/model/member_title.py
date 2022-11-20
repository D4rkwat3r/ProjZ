from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemberTitle:
    title_id: Optional[int] = None
    circle_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    type: Optional[int] = None
    visible: bool = False
    position: Optional[int] = None
    status: Optional[int] = None
