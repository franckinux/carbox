import asyncio
import os
import random
from ui import Inputs, GO_ON, NEW_TRACK, NEXT, PAUSE, PLAY, SHUTDOWN, WAY_POINT

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject as gobject

gobject.threads_init()

from sound_player import GstPlayer


class FileProvider:
    def __init__(self, config):
        self.path = config["directory"]
        self.extensions = config["extensions"].split(',')

        self.pieces = []

    def scan_directory(self):
        for dir_path, subdir_list, file_list in os.walk(self.path):
            for fname in file_list:
                full_path = os.path.join(dir_path, fname)
                try:
                    extension = full_path.split('.')[-1]
                except:
                    continue
                if extension in self.extensions:
                    self.pieces.append(full_path)

    def pick_file(self):
        if self.pieces:
            piece = random.choice(self.pieces)
            self.pieces.remove(piece)
            return piece
        else:
            return


class Judebox:
    def __init__(self, loop, queue, config):
        self.loop = loop
        self.queue = queue

        self.player = GstPlayer()
        self.player.register_callbacks(self.end)

        self.files = FileProvider(config)
        self.inputs = Inputs(5)

    def end(self):
        print("end")
        piece = self.files.pick_file()
        if piece:
            self.player.start(piece)

    async def roll(self):
        self.files.scan_directory()

        while True:
            action = self.inputs.read()
            if action == PLAY:
                piece = self.files.pick_file()
                if piece:
                    self.player.start(piece)
            elif action == PAUSE:
                self.player.pause()
            elif action == GO_ON:
                self.player.play()
            elif action == NEXT:
                self.player.close()
                piece = self.files.pick_file()
                if piece:
                    self.player.start(piece)
            # elif action == STOP:
            #     self.player.close()
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
