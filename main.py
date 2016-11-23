#!/usr/bin/python

import argparse
import asyncio
import configparser

from gps import GpsTracker
from judebox import Judebox


async def main(loop):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    queue = asyncio.Queue()

    judebox = Judebox(loop, queue, dict(config.items("judebox")))
    task1 = asyncio.ensure_future(judebox.roll())

    gps_tracker = GpsTracker(loop, queue, dict(config.items("gps")))
    task2 = asyncio.ensure_future(gps_tracker.track())

    await task1
    task2.cancel()
    await task2

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
