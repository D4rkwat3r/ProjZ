from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RichFormat:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class TextSpan:
        @dataclass_json(letter_case=LetterCase.CAMEL)
        @dataclass
        class Data:
            bold: Optional[bool] = None
            italic: Optional[bool] = None
            strikethrough: Optional[bool] = None
            underline: Optional[bool] = None
            foreground_color: Optional[str] = None
            background_color: Optional[str] = None
        start: Optional[int] = None
        end: Optional[int] = None
        data: Optional[Data] = None

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class ParagraphSpan:
        @dataclass_json(letter_case=LetterCase.CAMEL)
        @dataclass
        class Data:
            style: Optional[str] = None
            alignment: Optional[str] = None
        start: Optional[int] = None
        end: Optional[int] = None
        data: Optional[Data] = None

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class AttachmentSpan:
        @dataclass_json(letter_case=LetterCase.CAMEL)
        @dataclass
        class Data:
            @dataclass_json(letter_case=LetterCase.CAMEL)
            @dataclass
            class Link:
                url: Optional[str] = None
                custom_title: Optional[str] = None
                title: Optional[str] = None
                media_ref_id: Optional[int] = None
                editing_media_id: Optional[str] = None

            @dataclass_json(letter_case=LetterCase.CAMEL)
            @dataclass
            class Mention:
                uid: Optional[int] = None
                role_id: Optional[int] = None
                role_name_length: Optional[int] = None

            @dataclass_json(letter_case=LetterCase.CAMEL)
            @dataclass
            class Poll:
                poll_ref_id: Optional[int] = None

            @dataclass_json(letter_case=LetterCase.CAMEL)
            @dataclass
            class Media:
                media_ref_id: Optional[int] = None
            type: Optional[str] = None
            link: Optional[Link] = None
            mention: Optional[Mention] = None
            media: Optional[Media] = None
            poll: Optional[Poll] = None
            # other
        start: Optional[int] = None
        end: Optional[int] = None
        data: Optional[Data] = None
    version: Optional[int] = None
    text_spans: Optional[list[TextSpan]] = None
    paragraph_spans: Optional[list[ParagraphSpan]] = None
    attachment_spans: Optional[list[AttachmentSpan]] = None
