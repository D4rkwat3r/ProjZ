from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from .media import Media


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Sticker:
    sticker_id: int
    name: str
    media: Media
