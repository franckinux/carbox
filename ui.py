import os
import pigpio

GPIO_IN1 = 12
GPIO_IN2 = 25
GPIO_IN3 = 24
GPIO_IN4 = 23
GPIO_BUZZER = 18

SHUTDOWN = 0
PLAY = 1
PAUSE = 2
GO_ON = 3
NEXT = 4
WAY_POINT = 5
NEW_TRACK = 6


class Buzzer:
    def __init__(self):
        self.pi = pigpio.pi()

        # to stop it at start up if on !
        self.buzzer = True

    def start(self):
        if not self.buzzer:
            self.pi.set_PWM_dutycycle(GPIO_BUZZER, 128)
            self.pi.set_PWM_frequency(GPIO_BUZZER, 1000)
            self.buzzer = True

    def stop(self):
        if self.buzzer:
            self.pi.set_PWM_dutycycle(GPIO_BUZZER, 0)
            self.pi.set_PWM_frequency(GPIO_BUZZER, 0)
            self.buzzer = False

    def close(self):
        self.pi.stop()


class Inputs:
    def __init__(self, cycles):
        self.pi = pigpio.pi()
        self.cycles = cycles
        self.current_cycles = 0

        self.pi.set_mode(GPIO_IN1, pigpio.INPUT)
        self.pi.set_mode(GPIO_IN2, pigpio.INPUT)
        self.pi.set_mode(GPIO_IN3, pigpio.INPUT)
        self.pi.set_mode(GPIO_IN4, pigpio.INPUT)

    def read(self):
        if self.current_cycles == 0:
            i1 = self.pi.read(GPIO_IN1)
            i2 = self.pi.read(GPIO_IN2)
            i3 = self.pi.read(GPIO_IN3)
            i4 = self.pi.read(GPIO_IN4)
            sum = i1 + i2 + i3 + i4
            if sum == 1:
                if i1 == 1:
                    return PLAY
                elif i2 == 1:
                    return PAUSE
                elif i3 == 1:
                    return GO_ON
                elif i4 == 1:
                    return NEXT
            elif sum == 2:
                if i1 + i2 == 2:
                    return WAY_POINT
                if i2 + i3 == 2:
                    return NEW_TRACK
            elif sum == 4:
                os.system("sudo shutdown --halt --no-wall")
                return SHUTDOWN
            if sum != 0:
                self.current_cycles = self.cycles
        else:
            self.current_cycles -= 1

    def close(self):
        self.pi.stop()
