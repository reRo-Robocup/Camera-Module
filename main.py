import sensor, image, time, ulab
#from ulab import numpy

import ulab as np


#import numpy

sensor.reset(freq=29700000, set_regs=True, dual_buff=True)
#sensor.reset(freq=24000000, set_regs=True, dual_buff=True)
#sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

#usb = pyb.USB_VCP()

clock = time.clock()

threshold = [(0, 100, 12, 89, 22, 127)]

img_w = sensor.width()
img_h = sensor.height()

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

    #obj_degree = np.arctan2(cy, cx)
    obj_angle = np.atan(cy / cx)
    obj_angle *= (180 / 3.14)
    print(obj_angle)


while(True):
    try:
        clock.tick()
        img = sensor.snapshot()
        getCam(threshold)

    except (AttributeError, OSError, RuntimeError) as err:
        pass
