from typing import Optional


class PaginatedList(list):
    def __init__(self, original_list: list, pagination: Optional[dict] = None, next_page_token: Optional[str] = None):
        super().__init__(original_list)
        self.next_page_token = next_page_token or (None if pagination is None else pagination.get("nextPageToken"))
