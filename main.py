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

# P4-TX P5-RX

def sendData():
    # ヘッダー送信
    uart.writechar(0xFF);
    uart.writechar(0xFF);
    uart.writechar(0xFD);
    uart.writechar(0x00);

    data_angle = [289, 23, 315]

    _H = data_angle[0] >> 8
    _L = data_angle[0] & 0x00FF
    uart.writechar(_H)
    uart.writechar(_L)

    _H = data_angle[1] >> 8
    _L = data_angle[1] & 0x00FF
    uart.writechar(_H)
    uart.writechar(_L)

    _H = data_angle[2] >> 8
    _L = data_angle[2] & 0x00FF
    uart.writechar(_H)
    uart.writechar(_L)


while True:
    clock.tick()
    img = sensor.snapshot()
    sendData()
