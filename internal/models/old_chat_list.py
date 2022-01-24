class OldChatList(list):

    def __repr__(self) -> str:
        return f"<< OLD CHAT LIST OBJECT | SIZE: {len(self)} >>"

    def __init__(self, is_end: bool) -> None:
        super().__init__()
        self.is_end = is_end
