#!/usr/bin/python

import asyncio
import configparser
import gbulb

from gps import GpsTracker
from judebox import Judebox


async def main(loop):
    config = configparser.ConfigParser()
    config.read("config.ini")

    queue = asyncio.Queue()

    judebox = Judebox(loop, queue, dict(config.items("judebox")))
    task1 = asyncio.ensure_future(judebox.roll())

    gps_tracker = GpsTracker(loop, queue, dict(config.items("gps")))
    task2 = asyncio.ensure_future(gps_tracker.track())

    await task1
    task2.cancel()
    await task2

gbulb.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
