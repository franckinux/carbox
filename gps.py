import asyncio
from concurrent.futures import CancelledError
from micropyGPS import MicropyGPS
from serial_asyncio import create_serial_connection

micro_gps = MicropyGPS()


class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        for char in data:
            micro_gps.update(chr(char))


class GpsTracker:
    def __init__(self, config):
        self.config = config

    async def track(self, loop):
        coro = create_serial_connection(loop, Output, self.config["device"],
                                        baudrate=self.config["baudrate"])
        asyncio.ensure_future(coro)

        while True:
            try:
                await asyncio.sleep(3)
            except CancelledError:
                break
            print(micro_gps.altitude, micro_gps.latitude, micro_gps.longitude)
