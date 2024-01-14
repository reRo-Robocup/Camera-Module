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

header = [0xFF, 0xFF, 0xFD, 0x00]

def sendData(BallAngle, YelAngle, BlueAngle, BallDis, YelDis, BlueDis, BallTF, YelTF, BlueTF):
    # ヘッダー送信
    for i in range (4):
        uart.write(header[i])

    # 配列に代入
    Angles = [BallAngle, YelAngle, BlueAngle]
    Distance = [BallDis, YelDis, BlueDis]
    disable = [BallTF, YelTF, BlueTF]

    # Angles送信 16bit
    for i in range (3):
        _data_H = (Angles[i] & 0xFF00) >> 8
        _data_L = (Angles[i] & 0x00FF) >> 0
        uart.write(_data_H)
        uart.write(_data_L)

    # Distance送信 8bit
    for i in range (3):
        uart.write(Distance[i])

    # disable送信 1bit (下位5bit余り)
    _data = ((disable[0] >> 8) | (disable[1] >> 7) | (disable[2] >> 6)) | 0x0000
    uart.write(_data)

distance = 0
angle = 0

def getCam(threshold):
    pixels = [0]
    rectSpace = [0]
    cnt = 0
    dx = dy = a = angle = cnt = dictance = 0

    for blob in img.find_blobs(threshold, pixels_threshold = 100, area_threshold = 100, merge = True, margin = 10):
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

    return angle, dx, dy, a, cnt, distance

while True:
    try:
        clock.tick()
        img = sensor.snapshot()
        #data = getCam([(0, 100, -3, 15, -35, -13)])
        data = getCam([(0, 100, -128, 127, 17, 127)])
        dis = data[5]

        ball = -1

        if data[4] >= 0:
            ball = data[0]

        #print(ball,dis)

        if usb.isconnected():
            img.draw_cross(160,120,(0,0,0))
            img.draw_circle(160,120,120,(255,255,255))
            img.draw_line(160,120,data[1],data[2],(0,0,0))

        uartProtocol.sendData()

        uart.write(str(ball)+' '+str(dis)+'\0')
        # uart.write(str(ball)+' '+str(dis)+'\0')
        # uart.write(str(ball)+' '+str(dis)+'\0')

    except (ZeroDivisionError, RuntimeError, OSError, NameError) as err:
        if usb.isconnected():
            print(err)
        pass
