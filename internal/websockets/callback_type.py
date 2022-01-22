from types import FunctionType


class CallbackType:
    def __init__(self,
                 handler: FunctionType,
                 notification_type: str,
                 **extras):
        self.handler = handler
        self.notification_type = notification_type
        self.extras = extras
