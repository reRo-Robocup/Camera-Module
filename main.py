import math
import sensor, image, time

# import ulab as np
from machine import UART
from fpioa_manager import fm

sensor.reset(freq=29700000, set_regs=True, dual_buff=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

img_w = sensor.width()
img_h = sensor.height()

fm.register(35, fm.fpioa.UART1_RX, force=True)
fm.register(34, fm.fpioa.UART1_TX, force=True)
uart = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

clock = time.clock()

header = b"\xff\xff\xfd\x00"

def getCam(threshold):
    pixels_array = [0]
    cx_array = [0]
    cy_array = [0]
    index_id = 0
    enable = False

    for blob in img.find_blobs(
        threshold, pixels_threshold=20, area_threshold=20, merge=True, margin=10
    ):
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

    obj_angle = (math.atan2(cy, cx) * (180 / math.pi)) + 180
    obj_distance = math.sqrt(math.pow(cx, 2) + math.pow(cy, 2))

    return int(obj_angle), int(obj_distance), enable, int(cx), int(cy)


def sendData(_ang_array, _distace_array, _enable_array):
    uart.write(header)

    for i in range(3):
        uart.write(_ang_array[i].to_bytes(2, "little"))

    for i in range(3):
        uart.write(_distace_array[i].to_bytes(2, "little"))

    enable = 0
    for i in range(3):
        enable = enable | _enable_array[i] << i

    uart.write(enable.to_bytes(1, "little"))

orange = [(0, 100, 8, 60, 24, 58)]
blue = [(0, 100, -128, 127, -80, -34)]
yellow = [(0, 100, -128, 127, -80, -34)]

while True:
    try:
        clock.tick()
        img = sensor.snapshot()

        ball_data = getCam(orange)
        yell_data = getCam(yellow)
        blue_data = getCam(blue)

        ang_array = [ball_data[0], yell_data[0], blue_data[0]]
        dis_array = [ball_data[1], yell_data[1], blue_data[1]]
        enb_array = [ball_data[2], yell_data[2], blue_data[2]]

        sendData(ang_array, dis_array, enb_array)

        img.draw_line(
            int(img_w / 2),
            int(img_h / 2),
            int(ball_data[3] + (img_w / 2)),
            int(ball_data[4] + (img_h / 2)),
            (0, 0, 0),
            3,
        )

        # print(ball_data[0])
        # print(clock.fps())

    except (AttributeError, OSError, RuntimeError) as err:
        #print(err)
        pass
