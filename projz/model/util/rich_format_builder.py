from ..rich_format import RichFormat
from typing import Optional
from uuid import uuid4


class RichFormatBuilder:
    def __init__(self):
        self._fmt = RichFormat(4, [], [], [])

    def text_span(
            self,
            start: int,
            end: int,
            bold: bool = False,
            italic: bool = False,
            strikethrough: bool = False,
            underline: bool = False,
            foreground: Optional[str] = None,
            background: Optional[str] = None
    ) -> "RichFormatBuilder":
        self._fmt.text_spans.append(RichFormat.TextSpan(start, end, RichFormat.TextSpan.Data(
            bold, italic, strikethrough, underline, foreground, background
        )))
        return self

    def paragraph_span(self, start: int, end: int, style: Optional[str] = None, alignment: Optional[str] = None) -> "RichFormatBuilder":
        self._fmt.paragraph_spans.append(RichFormat.ParagraphSpan(start, end, RichFormat.ParagraphSpan.Data(style, alignment)))
        return self

    def bold(self, start: int, end: int) -> "RichFormatBuilder": return self.text_span(start, end, bold=True)

    def italic(self, start: int, end: int) -> "RichFormatBuilder": return self.text_span(start, end, italic=True)

    def strikethrough(self, start: int, end: int) -> "RichFormatBuilder": return self.text_span(start, end,strikethrough=True)

    def underline(self, start: int, end: int) -> "RichFormatBuilder": return self.text_span(start, end, underline=True)

    def foreground(self, start: int, end: int, color: str) -> "RichFormatBuilder": return self.text_span(start, end, foreground=color)

    def background(self, start: int, end: int, color: str) -> "RichFormatBuilder": return self.text_span(start, end, background=color)

    def h1(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, style="h1")

    def h2(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, style="h2")

    def h3(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, style="h3")

    def quote(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, style="quote")

    def left(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, alignment="left")

    def center(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, alignment="center")

    def right(self, start: int, end: int) -> "RichFormatBuilder": return self.paragraph_span(start, end, alignment="right")

    def link(
        self,
        start: int,
        url: str,
        custom_title: str = "",
        title: str = "",
        media_id: int = 0
    ) -> "RichFormatBuilder":
        self._fmt.attachment_spans.append(RichFormat.AttachmentSpan(start, start + 1, RichFormat.AttachmentSpan.Data(
            type="link",
            link=RichFormat.AttachmentSpan.Data.Link(url, custom_title, title, media_id, str(uuid4()))
        )))
        return self

    def mention(self, start: int, username: str, uid: int, role_id: int = 0,
                role_name_length: int = 0) -> "RichFormatBuilder":
        end = len(f"@{username}" if not username.startswith("@") else username)
        self._fmt.attachment_spans.append(RichFormat.AttachmentSpan(start, end, RichFormat.AttachmentSpan.Data(
            type="mention",
            mention=RichFormat.AttachmentSpan.Data.Mention(uid, role_id, role_name_length)
        )))
        return self

    def poll(self, start: int, poll_id: int) -> "RichFormatBuilder":
        self._fmt.attachment_spans.append(RichFormat.AttachmentSpan(start, start + 1, RichFormat.AttachmentSpan.Data(
            type="poll",
            poll=RichFormat.AttachmentSpan.Data.Poll(poll_id)
        )))
        return self

    def media(self, start: int, media_id: int) -> "RichFormatBuilder":
        self._fmt.attachment_spans.append(RichFormat.AttachmentSpan(start, start + 1, RichFormat.AttachmentSpan.Data(
            type="media",
            media=RichFormat.AttachmentSpan.Data.Media(media_id)
        )))
        return self

    def build(self) -> RichFormat:
        return self._fmt
