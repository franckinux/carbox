import asyncio
import os
import random
import select
import sys

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

    def end(self):
        piece = self.files.pick_file()
        if piece:
            self.player.start(piece)
        print("end")

    async def roll(self):
        self.files.scan_directory()

        print("1: exit")
        print("2: judebox start")
        print("3: judebox pause")
        print("4: judebox play")
        print("5: judebox close")
        print("6: gps waypoint")
        print("7: gps new track")

        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip()
                if line == '1':
                    self.player.close()
                    break
                elif line == '2':
                    print("start")
                    piece = self.files.pick_file()
                    if piece:
                        self.player.start(piece)
                elif line == '3':
                    print("pause")
                    self.player.pause()
                elif line == '4':
                    print("play")
                    self.player.play()
                elif line == '5':
                    print("close")
                    self.player.close()
                elif line == '6':
                    await self.queue.put("waypoint")
                elif line == '7':
                    await self.queue.put("track")
            await asyncio.sleep(0.5)
