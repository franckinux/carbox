import asyncio

from actions import NEXT, NEW_TRACK, STOP, SHUTDOWN, TOGGLE, WAY_POINT
from sound_player import MpdPlayer


class Judebox:
    def __init__(self, loop, queue, config, ui):
        self.loop = loop
        self.queue = queue
        self.ui = ui

        self.player = MpdPlayer()

    async def roll(self):
        try:
            await self.player.open()
        except:
            return

        while True:
            action = self.ui.input.read()
            if action == TOGGLE:
                await self.player.toggle()
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
                break

            await asyncio.sleep(0.5)
