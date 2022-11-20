from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from datetime import datetime
from .parse import time_field
from .parse import extensions_field
from .sticker import Sticker


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Category:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class TagInfo:
        @dataclass_json(letter_case=LetterCase.CAMEL)
        @dataclass
        class Style:
            background_color: Optional[str] = None
            text_color: Optional[str] = None
            border_color: Optional[str] = None
            solid_color: Optional[str] = None
        created_time: Optional[datetime] = time_field()
        tag_id: Optional[int] = None
        tag_name: Optional[str] = None
        title: Optional[str] = None
        lower_case_name: Optional[str] = None
        language_code: Optional[str] = None
        status: Optional[int] = None
        official_verified: Optional[int] = None
        tag_type: Optional[int] = None
        style: Optional[Style] = None
    created_time: Optional[datetime] = time_field()
    category_id: Optional[int] = None
    sticker_id: Optional[int] = None
    name: Optional[str] = None
    title: Optional[str] = None
    lower_case_name: Optional[str] = None
    content_region: Optional[int] = None
    status: Optional[int] = None
    object_type: Optional[int] = None
    score: Optional[int] = None
    sticker: Optional[Sticker] = None
    concept_id: Optional[int] = None
    concept_name: Optional[str] = None
    category_concept: Optional[int] = None
    tag_info: Optional[TagInfo] = None
    extensions: dict = extensions_field()
