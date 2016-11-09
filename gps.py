import asyncio
from concurrent.futures import CancelledError
from gpxdata import LatLon
from micropyGPS import MicropyGPS
from serial_asyncio import create_serial_connection

micro_gps = MicropyGPS()


class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        for char in data:
            micro_gps.update(chr(char))


def dm2deg(degree, minute, hemisphere):
    if hemisphere in "SsWw":
        sign = -1
    else:
        sign = 1
    return (degree + minute / 60) * sign


class GpsTracker:
    def __init__(self, config):
        self.baudrate = int(config["baudrate"])
        self.device = config["device"]
        self.distance = float(config["distance"])
        self.interval = int(config["interval"])

    async def track(self, loop):

        coro = create_serial_connection(loop, Output, self.device,
                                        baudrate=self.baudrate)
        asyncio.ensure_future(coro)

        last_point = curr_point = None
        track = []

        while True:
            try:
                while True:
                    await asyncio.sleep(self.interval)
                    if micro_gps.valid:
                        break
            except CancelledError:
                break

            curr_point = LatLon(
                dm2deg(*micro_gps.latitude), dm2deg(*micro_gps.longitude)
            )
            if last_point is None or \
               last_point.distance(curr_point) >= self.distance:
                last_point = curr_point
                track.append(curr_point)

        print(track)
