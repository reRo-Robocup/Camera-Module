# Dynamixel protocol 2.0

import pyb, ulab, sensor, time, image
from ulab import numpy as np

header = 0xFF

def sendData(BallAngle, BallDistance, Bangle, Bdis, Yangle, Ydis):
    uart.write(header)
    
    Ball_data_H = (BallAngle & 0x0000FF00) >> 8
    Ball_data_L = (BallAngle & 0xFF000000) >> 0