from .pagination import Pagination


class MessageList(list):

    def __repr__(self) -> str:
        return f"<< MESSAGE LIST OBJECT | SIZE: {len(self)} >>"

    def __init__(self, pagination: Pagination) -> None:
        super().__init__()
        self.pagination = pagination
