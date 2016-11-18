import asyncio
from ui import Inputs, NEW_TRACK, NEXT, PAUSE, PLAY, SHUTDOWN, STOP, WAY_POINT
from sound_player import MpdPlayer


class Judebox:
    def __init__(self, loop, queue, config):
        self.loop = loop
        self.queue = queue

        self.player = MpdPlayer()

        self.inputs = Inputs(5)

    async def roll(self):
        await self.player.open()

        while True:
            action = self.inputs.read()
            if action == PLAY:
                await self.player.play()
            elif action == PAUSE:
                await self.player.pause()
            elif action == NEXT:
                await self.player.next()
            elif action == STOP:
                await self.player.stop()
            elif action == WAY_POINT:
                await self.queue.put("waypoint")
            elif action == NEW_TRACK:
                await self.queue.put("track")
            elif action == SHUTDOWN:
                await self.queue.put("buzzer")
                self.player.close()
                self.inputs.close()
                break

            await asyncio.sleep(0.5)

        await self.player.close()
