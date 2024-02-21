import sensor, image, time
import ulab as np
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

    obj_angle = np.atan(cy / cx) * (180 / 3.14)
    obj_distance = np.sqrt(np.pow(cx, 2) + np.pow(cy, 2))
    
    # print(obj_angle, obj_distance, enable)
    return obj_angle, obj_distance, enable

def sendData(ang_array, distace_array, enable_array):
    for i in header:
        uart.writechar(header)


while(True):
    try:
        clock.tick()
        img = sensor.snapshot()
        ang = getCam(orange)

        for i in header:
            uart.writechar(i)

        data_H = ang >> 8
        data_L = data_H & 0x00FF

        uart.write(data_H)
        uart.write(data_L)

    except (AttributeError, OSError, RuntimeError) as err:
        pass
