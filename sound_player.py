import aiompd
import random


class MyMpdClient(aiompd.Client):

    @aiompd.helpers.lock
    async def set_random(self, value):
        assert type(value) == bool
        value = 1 if value else 0
        await self._send_command('random', value)

    @aiompd.helpers.lock
    async def set_consume(self, value):
        assert type(value) == bool
        value = 1 if value else 0
        await self._send_command('consume', value)

    @aiompd.helpers.lock
    async def list(self, type_):
        assert type_ in ("any", "base", "file", "modified-since")
        response = await self._send_command('list', type_)
        lines = response.decode("utf-8").split('\n')
        files = [file_ for file_ in lines if file_.startswith("file:")]
        return [file_.split(':')[1].lstrip() for file_ in files]


class MpdPlayer:
    def __init__(self):
        self.client = MyMpdClient()

    async def open(self):
        self.transport, _ = self.client.connect()

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
            await self.client.add(file_)
            playlist_length += 1

    async def play(self):
        await self.client.play()

    async def pause(self):
        await self.client.pause()

    async def stop(self):
        await self.client.stop()

    async def next(self):
        await self.next.next()

    async def close(self):
        self.transport.disconnect()
