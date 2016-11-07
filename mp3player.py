import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst as gst

GObject.threads_init()
gst.init(None)


class GstPlayer:
    def __init__(self):
        self.player = gst.ElementFactory.make("playbin", "player")

        self.ok = True
        if not self.player:
            self.ok = False
            return

        self.error_cb = None
        self.eos_cb = None

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::eos", self.on_eos)
        self.bus.connect("message::error", self.on_error)

    def register_callbacks(self, eos_cb, error_cb=None):
        self.eos_cb = eos_cb
        self.error_cb = error_cb

    def on_eos(self, bus, msg):
        self.player.set_state(gst.State.NULL)
        if self.eos_cb is not None:
            self.eos_cb()

    def on_error(self, bus, msg):
        if self.error_cb is not None:
            err, dbg = msg.parse_error()
            self.error_cb("ERROR:", msg.src.get_name(), ":", err.message)

    def start(self, mp3):
        self.player.set_property("uri", mp3)
        return self.play()

    def play(self):
        return self.player.set_state(gst.State.PLAYING) != gst.StateChangeReturn.FAILURE

    def pause(self):
        self.player.set_state(gst.State.PAUSED)

    def close(self):
        self.player.set_state(gst.State.NULL)
