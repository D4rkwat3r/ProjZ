from io import BytesIO


class CopyToBufferWriter:
    def __init__(self, buffer: BytesIO):
        self.buffer = buffer

    async def write(self, data: bytes):
        self.buffer.write(data)
