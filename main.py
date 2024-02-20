import sensor, image, time
import ulab as np
from machine import UART
from fpioa_manager import fm

#from modules import ws2812

sensor.reset(freq=29700000, set_regs=True, dual_buff=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

threshold = [(0, 100, 12, 89, 22, 127)]

img_w = sensor.width()
img_h = sensor.height()

header = [0xFF, 0xFF, 0xFD, 0x00]

fm.register(35, fm.fpioa.UART1_TX, force=True)
fm.register(34, fm.fpioa.UART1_RX, force=True)

uart = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

clock = time.clock()

def getCam(threshold):
    pixels_array = [0]
    cx_array = [0]
    cy_array = [0]
    id = 0

    for blob in img.find_blobs(threshold, pixels_threshold = 20, area_threshold = 20, merge = True, margin = 10):
        pixels_array.append(blob.pixels())
        cx_array.append(blob.cx())
        cy_array.append(blob.cy())

    max_pixels = max(pixels_array)
    id = pixels_array.index(max_pixels)

    cx = cx_array[id]
    cy = cy_array[id]

    cx -= img_w / 2
    cy -= img_h / 2

    if cx == 0:
        cx = 1
    if cy == 0:
        cy = 1

    obj_angle = np.atan(cy / cx)
    obj_angle *= (180 / 3.14)
    print(obj_angle)

    return obj_angle


while(True):
    try:
        clock.tick()
        img = sensor.snapshot()
        ang = getCam(threshold)

        for i in header:
            uart.writechar(i)

        data_H = ang >> 8
        data_L = data_H & 0x00FF

        uart.write(data_H)
        uart.write(data_L)

    except (AttributeError, OSError, RuntimeError) as err:
        pass
