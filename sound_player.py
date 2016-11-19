import aiompd
import random


class MpdPlayer:
    def __init__(self):
        self.client = aiompd.Client()

    async def open(self):
        self.transport, _ = await self.client.connect()

        # await self.client.clear()
        await self.client.set_random(False)
        await self.client.set_consume(True)

        files = await self.client.list("file")
        random.shuffle(files)

        status = await self.client.get_status()
        playlist_length = status.playlistlength

        while playlist_length < 30:
            try:
                file_ = files.pop()
            except:
                break
            await self.client.add('"' + file_ + '"')
            playlist_length += 1

    def close(self):
        self.transport.close()

    async def next(self):
        await self.client.next()

    async def pause(self):
        await self.client.pause()

    async def play(self):
        await self.client.play()

    async def stop(self):
        await self.client.stop()

    async def toggle(self):
        await self.client.toggle()
