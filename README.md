# Camera-Module

UnitV Camera (M12, OV7740)

MaixPy IDE v0.2.5

# How to USE

> [!CAUTION]
> ファームウェアの書き換えは自己責任でお願いします

ファーム書き込み方法、kflash-cliが必要。

```
$ sudo pip3 install kflash
$ kflash -b 1500000 -e ./UnitV_M12_OV7740_rewriteFirmware.bin
```

2回の再起動後、この画面が出たら成功

```
MicroPython v0.6.2-85-g23d09fbcc on 2024-03-03; Sipeed_M1 with kendryte-k210
Type "help()" for more information.

Current CPU Frequency:  546
Current KPU Frequency:  74
8388608
121472
init i2c:2 freq:100000
[MAIXPY]: find ov7740
[MAIXPY]: find ov sensor
```

# Links

[Update MaixPy firmware - Sipeed Wiki](https://wiki.sipeed.com/soft/maixpy/en/get_started/upgrade_maixpy_firmware.html "Update MaixPy firmware")