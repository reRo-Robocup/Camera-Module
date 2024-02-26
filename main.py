import math
import sensor, image, time
#import ulab as np
from machine import UART
from fpioa_manager import fm

sensor.reset(freq=29700000, set_regs=True, dual_buff=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

img_w = sensor.width()
img_h = sensor.height()

fm.register(35, fm.fpioa.UART1_TX, force=True)
fm.register(34, fm.fpioa.UART1_RX, force=True)
uart = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

clock = time.clock()

header = [0xFF, 0xFF, 0xFD, 0x00]

orange = [(0, 100, 12, 89, 22, 127)]
yellow = [(0)]
blue   = [(0)]

def getCam(threshold):
    pixels_array = [0]
    cx_array = [0]
    cy_array = [0]
    index_id = 0
    enable = False

    for blob in img.find_blobs(threshold, pixels_threshold = 20, area_threshold = 20, merge = True, margin = 10):
        pixels_array.append(blob.pixels())
        cx_array.append(blob.cx())
        cy_array.append(blob.cy())
        enable = True

    max_pixels = max(pixels_array)
    index_id = pixels_array.index(max_pixels)

    cx = cx_array[index_id] - (img_w / 2)
    cy = cy_array[index_id] - (img_h / 2)

    if cx == 0:
        cx = 1
    if cy == 0:
        cy = 1

    obj_angle = math.atan2(cy, cx)
    obj_distance = math.sqrt(math.pow(cx, 2) + math.pow(cy, 2))

    #print(obj_angle, obj_distance, enable)
    return int(obj_angle), int(obj_distance), enable, int(cx), int(cy)

def sendData(_ang_array, _distace_array, _enable_array):
    for i in header:
        uart.writechar(header)

    for i in range(3):
        _Hdata = _ang_array[i] << 8
        _Ldata = _Hdata & 0x00FF
        uart.writechar(_Hdata)
        uart.writechar(_Ldata)

    for i in range(3):
        _Hdata = _distace_array[i] << 8
        _Ldata = _Hdata & 0x00FF
        uart.writechar(_Hdata)
        uart.writechar(_Ldata)

    for i in range(3):
        _Hdata = _enable_array[i] << 8
        _Ldata = _Hdata & 0x00FF
        uart.writechar(_Hdata)
        uart.writechar(_Ldata)

orange = [(0, 100, 10, 66, 14, 50)]
blue = [(0, 100, -128, 127, -80, -34)]
yellow = [(0, 100, -128, 127, -80, -34)]

while(True):
    try:
        clock.tick()
        img = sensor.snapshot()

        ball_data = getCam(orange)
        yell_data = getCam(yellow)
        blue_data = getCam(blue)

        ang_array = [ball_data[0], yell_data[0], blue_data[0]]
        dis_array = [ball_data[1], yell_data[1], blue_data[1]]
        enb_array = [ball_data[2], yell_data[2], blue_data[2]]

        #sendData(ang_array, dis_array, enb_array)

        img.draw_line(int(img_w/2), int(img_h/2), int(ball_data[3] + (img_w / 2)), int(ball_data[4] + (img_h / 2)), (0,0,0), 3)

        #img.draw_line(0, 0, 100, 100, (0,255,0), 10)

        #print(ball_data[0])

    except (AttributeError, OSError, RuntimeError) as err:
        pass
