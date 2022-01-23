from .pagination import Pagination


class ChatList(list):

    def __repr__(self) -> str:
        return f"<< CHAT LIST OBJECT | SIZE: {len(self)} >>"

    def __init__(self, pagination: Pagination) -> None:
        super().__init__()
        self.pagination = pagination
