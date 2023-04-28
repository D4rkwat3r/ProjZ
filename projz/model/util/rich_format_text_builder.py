from .rich_format_builder import RichFormatBuilder
from ..rich_format import RichFormat


class RichFormatTextBuilder:
    def __init__(self):
        self._builder = RichFormatBuilder()
        self._current_offset = 0
        self._text = ""

    def _update_state(self, text: str) -> "RichFormatTextBuilder":
        self._text += text
        self._current_offset = len(self._text)
        return self

    def _update_increment(self) -> "RichFormatTextBuilder":
        self._current_offset += 1
        return self

    def bold(self, text: str) -> "RichFormatTextBuilder":
        self._builder.bold(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def italic(self, text: str) -> "RichFormatTextBuilder":
        self._builder.italic(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def strikethrough(self, text: str) -> "RichFormatTextBuilder":
        self._builder.strikethrough(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def underline(self, text: str) -> "RichFormatTextBuilder":
        self._builder.underline(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def foreground(self, text: str, color: str) -> "RichFormatTextBuilder":
        self._builder.foreground(self._current_offset, self._current_offset + len(text), color)
        return self._update_state(text)

    def background(self, text: str, color: str) -> "RichFormatTextBuilder":
        self._builder.background(self._current_offset, self._current_offset + len(text), color)
        return self._update_state(text)

    def h1(self, text: str) -> "RichFormatTextBuilder":
        self._builder.h1(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def h2(self, text: str) -> "RichFormatTextBuilder":
        self._builder.h2(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def h3(self, text: str) -> "RichFormatTextBuilder":
        self._builder.h3(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def quote(self, text: str) -> "RichFormatTextBuilder":
        self._builder.quote(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def left(self, text: str) -> "RichFormatTextBuilder":
        self._builder.left(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def center(self, text: str) -> "RichFormatTextBuilder":
        self._builder.center(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def right(self, text: str) -> "RichFormatTextBuilder":
        self._builder.right(self._current_offset, self._current_offset + len(text))
        return self._update_state(text)

    def link(self, url: str, custom_title: str = "", title: str = "", media_id: int = 0) -> "RichFormatTextBuilder":
        self._builder.link(self._current_offset, url, custom_title, title, media_id)
        return self._update_increment()

    def mention(self, username: str, uid: int, role_id: int = 0, role_name_length: int = 0) -> "RichFormatTextBuilder":
        self._builder.mention(self._current_offset, username, uid, role_id, role_name_length)
        return self._update_increment()

    def poll(self, poll_id: int) -> "RichFormatTextBuilder":
        self._builder.poll(self._current_offset, poll_id)
        return self._update_increment()

    def media(self, media_id: int) -> "RichFormatTextBuilder":
        self._builder.media(self._current_offset, media_id)
        return self._update_increment()

    def build(self) -> tuple[RichFormat, str]:
        return self._builder.build(), self._text
