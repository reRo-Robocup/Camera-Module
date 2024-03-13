#
#   main.py
#
#   Created on: 2024/1/5
#
#   Author: onlydcx, G4T1PR0
#

import math, sensor, image, time
import Maix, gc

from machine import UART
from fpioa_manager import fm

cpu_freq = 550
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

sensor.reset(freq=24000000, set_regs=True, dual_buff=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
#sensor.set_vflip(True)

sensor.set_saturation(2)
#sensor.set_contrast(-2)
#sensor.set_brightness(1)

img_w = sensor.width()
img_h = sensor.height()
mirror_cx = 179
mirror_cy = 126

fm.register(35, fm.fpioa.UART1_RX, force=True)
fm.register(34, fm.fpioa.UART1_TX, force=True)
uart = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000)

clock = time.clock()

header = b"\xff\xff\xfd\x00"


def getCam(threshold, obj_id):
    pixels_array = [0]
    cx_array = [0]
    cy_array = [0]
    x_array = [0]
    y_array = [0]
    w_array = [0]
    h_array = [0]
    index_id = 0
    enable = False

    for blob in img.find_blobs(
        threshold, pixels_threshold=5, area_threshold=5, merge=True, margin=10
    ):
        pixels_array.append(blob.pixels())
        cx_array.append(blob.cx())
        cy_array.append(blob.cy())
        x_array.append(blob.x())
        y_array.append(blob.y())
        w_array.append(blob.w())
        h_array.append(blob.h())
        enable = True

    max_pixels = max(pixels_array)
    index_id = pixels_array.index(max_pixels)

    cx = cx_array[index_id] - (mirror_cx)
    cy = cy_array[index_id] - (mirror_cy)

    edge_x_L = x_array[index_id] - (mirror_cx)
    edge_x_R = edge_x_L + w_array[index_id]

    edge_y_L = y_array[index_id] - (mirror_cy)
    edge_y_R = edge_y_L + h_array[index_id]
    
    w = w_array[index_id]
    h = h_array[index_id]

    if cx == 0 and cy == 0:
        obj_angle = 361
        obj_distance = 0
    elif cx == 0:
        obj_angle = 90 if (cy > 0) else 270
        obj_distance = cy
    elif cy == 0:
        obj_angle = 180 if (cx > 0) else 0
        obj_distance = cx
    else:
        obj_angle = 360 - ((math.atan2(cy, cx) * (180 / math.pi)) + 180)
        obj_distance = math.sqrt(math.pow(cx, 2) + math.pow(cy, 2))

    obj_angle = obj_angle - 180
    if(obj_angle < 0):
        obj_angle = obj_angle + 360

    R_dir = edge_y_R > 0
    L_dir = edge_y_L < 0
    
    isFront = R_dir and L_dir
    
    if debug_flag[obj_id]:
        if isFront:
            img.draw_line(int(mirror_cx),int(mirror_cy),int(mirror_cx + cx),int(mirror_cy + cy),(0, 255, 0),3,)
            
        else:
            img.draw_line(int(mirror_cx),int(mirror_cy),int(mirror_cx + cx),int(mirror_cy + cy),(255, 0, 0),3,)
            
        img.draw_line(int(mirror_cx),int(mirror_cy),int(mirror_cx + edge_x_L),int(mirror_cy + edge_y_L),(255, 255, 255),2,)
        img.draw_line(int(mirror_cx),int(mirror_cy),int(mirror_cx + edge_x_R),int(mirror_cy + edge_y_R),(255, 255, 255),2,)

        img.draw_cross(mirror_cx + cx,          mirror_cy + cy,         (0,0,0),5,2)
        img.draw_cross(mirror_cx + edge_x_L,    mirror_cy + edge_y_L,   (0,0,0),5,2)
        img.draw_cross(mirror_cx + edge_x_R,    mirror_cy + edge_y_R,   (0,0,0),5,2)
        img.draw_rectangle(edge_x_L + mirror_cx, edge_y_L + mirror_cy, w, h, (127,127,127) ,1,)

    return int(obj_angle), int(abs(obj_distance)), enable, int(cx), int(cy), isFront

def sendData(_ang_array, _distace_array, _enable_array):
    uart.write(header)

    for i in range(3):
        uart.write(_ang_array[i].to_bytes(2, "little"))

    for i in range(3):
        uart.write(_distace_array[i].to_bytes(2, "little"))

    enable = 0
    for i in range(6):
        enable = enable | _enable_array[i] << i

    uart.write(enable.to_bytes(1, "little"))

orange = [(51, 70, 18, 52, 36, 127)]
blue = [(0, 100, -118, 127, -111, -38)]
yellow = [(0, 100, -128, 16, 39, 127)]

debug_flag = [0,0,0]

while True:
    try:
        clock.tick()
        img = sensor.snapshot()

        ball_data = getCam(orange, 0)
        yell_data = getCam(yellow, 1)
        blue_data = getCam(blue, 2)

        ang_array = [ball_data[0], yell_data[0], blue_data[0]]
        dis_array = [ball_data[1], yell_data[1], blue_data[1]]
        tf_array = [ball_data[2], yell_data[2], blue_data[2],
                    ball_data[5], yell_data[5], blue_data[5]]

        sendData(ang_array, dis_array, tf_array)

    except (OSError, RuntimeError, AttributeError) as err:
        # print(err)
        pass
