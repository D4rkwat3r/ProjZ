from dataclasses import dataclass


@dataclass
class Pagination:
    next_page_token: str
    total: int
