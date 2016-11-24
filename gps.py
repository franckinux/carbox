import asyncio
from concurrent.futures import CancelledError
import csv
import datetime
from gpxdata import Document, LatLon, Point, Track, TrackSegment, Waypoint
import kdtree
from micropyGPS import MicropyGPS
import os
from serial_asyncio import create_serial_connection

micro_gps = MicropyGPS()


class DangerZones:
    def __init__(self, config):
        self.directory = config["danger-directory"]
        self.country = config["country"]

        self.tree = None

    def load(self):
        if os.path.isdir(self.directory):
            points = []
            for zone in os.listdir(self.directory):
                if zone.startswith(self.country) and zone.endswith(".csv"):
                    with open(os.path.join(self.directory, zone)) as csvfile:
                        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                        for row in reader:
                            points.append((float(row[1]), float(row[0])))

            self.tree = kdtree.create(points)

    def find_nearest(self, point):
        if self.tree is None:
            return
        node, _ = self.tree.search_nn((point.lat, point.lon))
        return LatLon(node.data[0], node.data[1])


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
            document.append(wp)

        # write or overwrite gpx file
        f = open(gpx_file, "wb")
        f.write(document.toGPX().toprettyxml(encoding="utf-8"))
        f.close()

        self.track_points = []
        self.way_points = []


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
    def __init__(self, loop, queue, config, ui):
        self.loop = loop
        self.queue = queue
        self.ui = ui

        self.baudrate = int(config["baudrate"])
        self.device = config["device"]
        self.distance = float(config["tracking-distance"])
        self.interval = int(config["tracking-interval"])
        self.danger_distance = float(config["danger-distance"])

        self.gpx_document = GpxDocument(config)
        self.danger = DangerZones(config)
        self.waiting_device = True
        self.control_task = asyncio.ensure_future(self.control())

    async def control(self):
        while True:
            try:
                command = await self.queue.get()
            except CancelledError:
                break
            if command == "buzzer":
                self.ui.buzzer.start()
            elif not self.waiting_device:
                if command == "waypoint":
                    if micro_gps.valid:
                        self.gpx_document.add_way_point(
                            Waypoint(
                                dm2deg(*micro_gps.latitude),
                                dm2deg(*micro_gps.longitude)
                            )
                        )
                elif command == "track":
                    self.gpx_document.save()

    async def close(self):
        self.control_task.cancel()
        await self.control_task

    async def track(self):
        while not os.path.exists(self.device):
            try:
                await asyncio.sleep(1)
            except CancelledError:
                await self.close()
                return
        self.waiting_device = False
        coro = create_serial_connection(self.loop, Output, self.device,
                                        baudrate=self.baudrate)
        asyncio.ensure_future(coro)

        self.danger.load()
        last_point = None

        while True:
            try:
                while True:
                    await asyncio.sleep(self.interval)
                    if micro_gps.valid:
                        break
            except CancelledError:
                await self.close()
                break

            curr_point = Point(
                dm2deg(*micro_gps.latitude), dm2deg(*micro_gps.longitude),
                ele=micro_gps.altitude,
                t=datetime.datetime.now()
            )

            # tracking feature
            if last_point is None or \
               last_point.distance(curr_point) >= self.distance:
                last_point = curr_point
                self.gpx_document.add_track_point(curr_point)

            # danger zone feature
            danger_point = self.danger.find_nearest(curr_point)
            if danger_point is not None and \
               danger_point.distance(curr_point) <= self.danger_distance:
                self.ui.buzzer.start()
                # print("danger !!! ", danger_point.lat, danger_point.lon)
            else:
                self.ui.buzzer.stop()

        self.gpx_document.save()
