import math
import sensor, image, time
from machine import UART
from fpioa_manager import fm
import Maix, gc

cpu_freq = 600
pll1 = 1200
kpu_div = 16

print("Current CPU Frequency: ", Maix.freq.get_cpu())
if (abs(cpu_freq - Maix.freq.get_cpu())) > 10:
    print("CPU Frequency is not " + str(cpu_freq) + "MHz!")
    print("Set it to " + str(cpu_freq) + "MHz...")
    Maix.freq.set(cpu=cpu_freq, pll1=100, kpu_div=1)

print("Current KPU Frequency: ", Maix.freq.get_kpu())
if (abs((pll1 / kpu_div) - Maix.freq.get_kpu())) > 5:
    print("KPU Frequency is not " + str((pll1 / kpu_div)) + "MHz!")
    print("Set it to " + str((pll1 / kpu_div)) + "MHz...")
    Maix.freq.set(cpu=cpu_freq, pll1=pll1, kpu_div=kpu_div)

Maix.utils.gc_heap_size(0x800000)
print(Maix.utils.gc_heap_size())
print(gc.mem_free())

# sensor.reset(freq=29700000, set_regs=True, dual_buff=True)
sensor.reset(freq=24000000, set_regs=True, dual_buff=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# sensor.set_jb_quality(100)

img_w = sensor.width()
img_h = sensor.height()
mirror_cx = 179
mirror_cy = 126

fm.register(35, fm.fpioa.UART1_RX, force=True)
fm.register(34, fm.fpioa.UART1_TX, force=True)
uart = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000)

clock = time.clock()

header = b"\xff\xff\xfd\x00"

# sensor.set_brightness(0)
# sensor.set_saturation(2)


def getCam(threshold):
    pixels_array = [0]
    cx_array = [0]
    cy_array = [0]
    index_id = 0
    enable = False

    for blob in img.find_blobs(
        threshold, pixels_threshold=10, area_threshold=20, merge=True, margin=10
    ):
        pixels_array.append(blob.pixels())
        cx_array.append(blob.cx())
        cy_array.append(blob.cy())
        enable = True

    max_pixels = max(pixels_array)
    index_id = pixels_array.index(max_pixels)

    cx = cx_array[index_id] - (mirror_cx)
    cy = cy_array[index_id] - (mirror_cy)

    if cx == 0 and cy == 0:
        obj_angle = 361
        obj_distance = 0
    elif cx == 0:
        obj_angle = 90 if (cy > 0) else 270
        obj_distance = cy
    elif cy == 0:
        obj_angle = 0 if (cx > 0) else 180
        obj_distance = cx
    else:
        obj_angle = 360 - ((math.atan2(cy, cx) * (180 / math.pi)) + 180)
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


orange = [(0, 100, 11, 127, 26, 126)]
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

        # img.draw_line(
        #     int(mirror_cx),
        #     int(mirror_cy),
        #     int(ball_data[3] + mirror_cx),
        #     int(ball_data[4] + mirror_cy),
        #     (0, 0, 0),
        #     3,
        # )

        # img.draw_cross(mirror_cx,mirror_cy,(255,255,255),5,2)

        # print(ball_data[0])
        # print(clock.fps())

    except (AttributeError, OSError, RuntimeError) as err:
        # print(err)
        pass
