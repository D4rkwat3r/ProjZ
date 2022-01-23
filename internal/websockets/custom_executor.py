from concurrent.futures.thread import ThreadPoolExecutor
import concurrent


class CustomExecutor(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        self._shutdown = False
        super().__init__(*args, **kwargs)

    def submit(self, *args, **kwargs):
        # This flag is useless and does not correspond to its name.
        # It provokes unpredictable behavior of the program.
        concurrent.futures.thread._shutdown = False
        return super().submit(*args, **kwargs)
