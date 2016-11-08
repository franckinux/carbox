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


async def poll(loop):
    coro = create_serial_connection(loop, Output, '/dev/ttyACM0', baudrate=115200)
    asyncio.ensure_future(coro)

    while True:
        try:
            await asyncio.sleep(3)
            print(micro_gps.altitude, micro_gps.latitude, micro_gps.longitude)
        except CancelledError:
            break
