import asyncio
import os
import random
import select
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject as gobject

gobject.threads_init()

from mp3player import GstPlayer


class FileProvider:
    def __init__(self, path):
        self.path = path
        self.mp3s = []

    def scan_directory(self):
        for dir_path, subdir_list, file_list in os.walk(self.path):
            for fname in file_list:
                full_path = os.path.join(dir_path, fname)
                if full_path.endswith(".mp3"):
                    self.mp3s.append(full_path)

    def pick_file(self):
        if self.mp3s:
            mp3 = random.choice(self.mp3s)
            self.mp3s.remove(mp3)
            return mp3
        else:
            return


class Judebox:
    def __init__(self, loop, queue, config):
        self.loop = loop
        self.queue = queue

        self.player = GstPlayer()
        self.player.register_callbacks(self.end)

        self.files = FileProvider(config["directory"])

    def end(self):
        mp3 = self.files.pick_file()
        if mp3:
            self.player.start(mp3)
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
                    mp3 = self.files.pick_file()
                    if mp3:
                        self.player.start(mp3)
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
