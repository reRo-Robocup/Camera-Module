import sensor, time, image, pyb, ulab
from ulab import numpy as np

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_contrast(100)
sensor.set_brightness(1)
sensor.skip_frames(30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

usb = pyb.USB_VCP()
clock = time.clock()
uart = pyb.UART(3, 19200)
uart.init(115200, bits=8, parity=None, stop=1)

header = (0xFF, 0xFF, 0xFD, 0x00)

# P4-TX P5-RX

def sendData(angles, distances, enables):
    size = 10
    send_data = [0x00] * size
    
    for i in header:
        send_data[i] = header
        
    for i in angles:
        _H = angles[i] >> 8
        _L = angles[i] & 0x00FF
        send_data[4+i] = _H
        send_data[4+i] = _L
        
    for i in range(size):
        uart.writechar(send_data[size])
        
orange = []
blue = []
yellow = []

while True:
    clock.tick()
    img = sensor.snapshot()
    
    for blob in img.find_blobs(threshold, pixel_threshold=100, area_threshold=100, merge=true,margin=10):
        
    
    sendData()