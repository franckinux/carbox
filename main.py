#!/usr/bin/python

import argparse
import asyncio
import configparser

from gps import GpsTracker
from judebox import Judebox


class Ui:
    def __init__(self, input_, buzzer):
        self.input = input_
        self.buzzer = buzzer


async def main(loop):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    queue = asyncio.Queue()

    target = dict(config.items("common"))["target"]
    if target == "raspberry-pi":
        from raspberrypi_ui import RealBuzzer as Buzzer, TouchkeyInput as Input
    elif target == "notebook":
        from notebook_ui import FakeBuzzer as Buzzer, KeyboardInput as Input
    else:
        return

    ui = Ui(Input(), Buzzer())

    judebox = Judebox(loop, queue, dict(config.items("judebox")), ui)
    task1 = asyncio.ensure_future(judebox.roll())

    gps_tracker = GpsTracker(loop, queue, dict(config.items("gps")), ui)
    task2 = asyncio.ensure_future(gps_tracker.track())

    await task1
    task2.cancel()
    await task2

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
