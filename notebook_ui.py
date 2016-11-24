import os
import select
import sys

from actions import NEXT, NEW_TRACK, STOP, SHUTDOWN, TOGGLE, WAY_POINT


class FakeBuzzer:
    def __init__(self):
        self.buzzer = False

    def start(self):
        if not self.buzzer:
            self.buzzer = True
            print("Buzzer on !")

    def stop(self):
        if self.buzzer:
            self.buzzer = False
            print("Buzzer off !")

    def close(self):
        pass


class KeyboardInput:
    def __init__(self, *args, **kwargs):
        pass

    def read(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline().strip().lower()
            if line == 't':
                return TOGGLE
            elif line == 'n':
                return NEXT
            elif line == 's':
                return STOP
            elif line == 'w':
                return WAY_POINT
            elif line == 'r':
                return NEW_TRACK
            elif line == 'u':
                os.system("sudo shutdown --halt --no-wall")
                return SHUTDOWN

    def close(self):
        pass
