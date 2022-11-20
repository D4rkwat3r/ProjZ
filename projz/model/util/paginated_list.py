from typing import Optional


class PaginatedList(list):
    def __init__(self, original_list: list, pagination: Optional[dict]):
        super().__init__(original_list)
        self.next_page_token = None if pagination is None else pagination.get("nextPageToken")
