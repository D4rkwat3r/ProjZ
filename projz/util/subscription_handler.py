from typing import Callable
from typing import Any
from uuid import uuid4
from inspect import iscoroutinefunction
from asyncio import create_task


class SubscriptionHandler:
    def __init__(self):
        self._subscriptions = []

    def subscribe(
        self,
        handler: Callable[[Any], Any],
        content_filter: Callable[[Any], bool] = lambda _: True,
        content_transform: Callable[[Any], Any] = lambda x: x
    ) -> str:
        subscription_id = str(uuid4())
        self._subscriptions.append({
            "id": subscription_id,
            "handler": handler,
            "filter": content_filter,
            "transform": content_transform
        })
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        try:
            self._subscriptions.remove(next(handler for handler in self._subscriptions if handler["id"] == subscription_id))
            return True
        except (StopIteration, ValueError):
            return False

    def broadcast(self, content: Any):
        for subscription in self._subscriptions:
            transformed_content = subscription["transform"](content)
            if not subscription["filter"](transformed_content):
                continue
            create_task(subscription["handler"](transformed_content)) \
                if iscoroutinefunction(subscription["handler"]) \
                else subscription["handler"](transformed_content)
