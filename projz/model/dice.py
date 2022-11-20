from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .media import Media


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Dice:
    dice_id: Optional[int] = None
    name: Optional[str] = None
    icon: Optional[Media] = None
    animation: Optional[Media] = None
    sides: Optional[list[Media]] = None
