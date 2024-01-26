# Dynamixel protocol 2.0

import pyb
uart = pyb.UART(3, 19200)
header = 0xFF

def sendData(BallAngle, YelAngle, BlueAngle, BallDis, YelDis, BlueDis, BallTF, YelTF, BlueTF):
    # ヘッダー送信
    uart.write(header)
    
    # 配列に代入
    Angles = [BallAngle, YelAngle, BlueAngle]
    Distance = [BallDis, YelDis, BlueDis]
    disable = [BallTF, YelTF, BlueTF]
    
    # Angles送信 16bit
    for i in range (3):
        _data_H = (Angles[i] & 0xFF00) >> 8
        _data_L = (Angles[i] & 0x00FF) >> 0
        uart.write(_data_H)_
        uart.write(_data_L)
        
    # Distance送信 8bit
    for i in range (3):
        uart.write(Distance[i])
        
    # disable送信 1bit (下位5bit余り)
    _data = ((disable[0] >> 8) | (disable[1] >> 7) | (disable[2] >> 6)) | 0x0000
    uart.write(_data)