import asyncio
from concurrent.futures import CancelledError
import datetime
from gpxdata import Document, LatLon, Track, TrackSegment, Waypoint
from micropyGPS import MicropyGPS
import os
from serial_asyncio import create_serial_connection

micro_gps = MicropyGPS()


class GpxDocument:
    def __init__(self, config):
        self.directory = config["gpx-directory"]

        self.track_points = []
        self.way_points = []

    def add_track_point(self, p):
        self.track_points.append(p)

    def add_way_point(self, wp):
        self.way_points.append(wp)

    def save(self):
        # create gpx document from existing gpx file
        today = datetime.date.today().strftime("%Y-%m-%d")
        gpx_file = os.path.join(self.directory, today + '.xml')
        document = Document(children=[], name=today)
        if os.path.exists(gpx_file):
            document = document.readGPX(gpx_file)

        # add track to document
        segment = TrackSegment(points=self.track_points)
        document.append(Track(segments=[segment]))

        # add way points to document
        for wp in self.way_points:
            document.append(Waypoint(wp[0], wp[1]))

        # write or overwrite gpx file
        f = open(gpx_file, "wb")
        f.write(document.toGPX().toprettyxml(encoding="utf-8"))
        f.close()


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

        self.gpx_document = GpxDocument(config)

    async def track(self, loop):

        coro = create_serial_connection(loop, Output, self.device,
                                        baudrate=self.baudrate)
        asyncio.ensure_future(coro)

        last_point = None

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
                self.gpx_document.add_track_point(curr_point)

        self.gpx_document.save()
