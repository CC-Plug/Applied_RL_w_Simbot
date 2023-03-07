#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
from matplotlib import pyplot as plt1
from matplotlib import pyplot as plt2
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import random
import pandas as pd

dataplot1 = []
dataplot2 = []

class RL_Robot(Robot):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 0
        pass
    
    def update(self):
        r = random.randint(0, 3)
        self.move(5)
        if r == 1:
            self.turn(15)
        elif r == 2:
            self.turn(-15)

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=RL_Robot, num_robots=1)
    app.run()