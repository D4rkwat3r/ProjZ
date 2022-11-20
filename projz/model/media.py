from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses import dataclass
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Media:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class Resource:
        width: int
        height: int
        url: str
        thumbnail: bool = False
        duration: int = 0
    base_url: str
    resource_list: list[Resource]
    media_id: Optional[int] = None
