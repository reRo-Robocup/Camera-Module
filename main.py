import sensor, time, image, pyb, ulab, machine
from ulab import numpy as np

sensor.reset(freq=29700000, set_regs=True, dual_buff=True)

sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
# sensor.set_framesize(sensor.VGA)

# -2 ~ +2
sensor.set_contrast(0)
sensor.set_brightness(0)
sensor.set_saturation(0)

sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# IDEに送信するクオリティ, 0~100
sensor.set_jb_quality(0)

sensor.skip_frames(30)

usb = pyb.USB_VCP()
clock = time.clock()

uart = pyb.UART(3, 19200)
uart.init(115200, bits=8, parity=None, stop=1)

LED = pyb.LED(2)

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

def getCam(threshold):
    pixels = [0]
    rectSpace = [0]
    cnt = 0
    dx = dy = a = angle = cnt = dictance = 0

    for blob in img.find_blobs(threshold, pixels_threshold = 20, area_threshold = 20, merge = True, margin = 10):
        pixels.append(blob.pixels())
        rectSpace.append(blob.rect())
        cnt += 1

    maxVal = max(pixels)
    num = pixels.index(maxVal)

    if cnt > 0:
        dx = rectSpace[num][0] + int(rectSpace[num][2] / 2)
        dy = rectSpace[num][1] + int(rectSpace[num][3] / 2)
        distance = int(np.sqrt(pow(160 - dx,2) + pow(120 - dy,2)))
        angle = 90 - int(np.degrees(np.arctan2(120 - dy,dx - 160)))
        a = (120 - dy) / (dx - 160)
        if angle < 0:
            angle += 360

    return angle, distance, dx, dy


cnt = 0

while True:
    try:
        LED.toggle()

        clock.tick()
        img = sensor.snapshot()


        data = getCam([(0, 100, 12, 89, 22, 127)])

        print(data[0], data[1])

        if usb.isconnected():
            img.draw_cross(160,120,(0,0,0))
            img.draw_circle(160,120,120,(255,255,255))
            img.draw_line(160,120,data[2],data[3],(0,0,0))


        for i in header:
            uart.writechar(i)

        hdata = data[0] >> 8
        ldata = data[0] & 0x00FF
        uart.writechar(hdata)
        uart.writechar(ldata)

        hdata = data[1] >> 8
        ldata = data[1] & 0x00FF
        uart.writechar(hdata)
        uart.writechar(ldata)

    except (ZeroDivisionError, RuntimeError, OSError, NameError) as err:
        if usb.isconnected():
            print(err)
        pass
