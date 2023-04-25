from io import BytesIO
from asyncio import get_running_loop


class CopyToBufferWriter:
    def __init__(self, buffer: BytesIO):
        self.buffer = buffer

    async def write(self, data: bytes):
        await get_running_loop().run_in_executor(None, self.buffer.write, data)
