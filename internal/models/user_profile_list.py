from .pagination import Pagination


class UserProfileList(list):

    def __repr__(self) -> str:
        return f"<< USER PROFILE LIST OBJECT | SIZE: {len(self)} >>"

    def __init__(self, pagination: Pagination) -> None:
        super().__init__()
        self.pagination = pagination
