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
sensor.set_vflip(False)
sensor.set_hmirror(True)

usb = pyb.USB_VCP()
clock = time.clock()
uart = pyb.UART(3, 19200)
uart.init(115200, bits=8, parity=None, stop=1)

header = (0xFF, 0xFF, 0xFD, 0x00)

# P4-TX P5-RX

def sendData(angles, distances, enables):
    
    # ヘッダー送信
    for i in header:
        uart.writechar(header)
        
    for i in angles:
        _H = angles[i] >> 8
        _L = angles[i] & 0x00FF
        uart.writechar(_H)
        uart.writechar(_L)
    
    for i in distances:
        uart.writechar(distances[i])
    
    _data = 0x00
    for i in enables:
        _data = _data & enables[i]


while True:
    clock.tick()
    img = sensor.snapshot()
    
    for blob in img.find_blobs(threshold, pixel_threshold=100, area_threshold=100, merge=true,margin=10):
        pixels.append(blob.pixels())
        rectSpace.append(blob.rect())
    
    sendData()