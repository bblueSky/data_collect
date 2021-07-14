#!/usr/bin/python3

import numpy as np
import cv2
from ctypes import *
import os.path
import sys
import os
os.environ['path'] += ';..\\..\\KSJApi.Bin\\x64';
def read(index_cam=0):
    libKsj = WinDLL("KSJApi64.dll")

    libKsj.KSJ_Init()

    camCount = libKsj.KSJ_DeviceGetCount()
    print("cam count: %d" % (camCount))

    usDeviceType = c_int()
    nSerials = c_int()
    usFirmwareVersion = c_int()
    libKsj.KSJ_DeviceGetInformation(index_cam, byref(usDeviceType), byref(nSerials), byref(usFirmwareVersion)) ##
    print("Device Type = %d" % (usDeviceType.value))
    print("Serials = %d" % (nSerials.value))
    print("FirmwareVersion = %d" % (usFirmwareVersion.value))

    nWidth = c_int()
    nHeight = c_int()
    nBitCount = c_int()
    libKsj.KSJ_CaptureGetSizeEx(index_cam, byref(nWidth), byref(nHeight), byref(nBitCount)) ##
    print("width = %d" % (nWidth.value))
    print("height = %d" % (nHeight.value))
    print("bitcount = %d" % (nBitCount.value))

    trigermode = c_int();
    libKsj.KSJ_TriggerModeGet(index_cam, byref(trigermode)) ##
    print("trigermode =  {0}".format(trigermode.value))

    nbufferSize = nWidth.value * nHeight.value * nBitCount.value / 8
    pRawData = create_string_buffer(int(nbufferSize))

    retValue = libKsj.KSJ_CaptureRgbData(index_cam, pRawData) ##

    if retValue != 1:
        print("capture error code %d" % (retValue))
    else:
        print("capture ok!")
        image = np.fromstring(pRawData, np.uint8).reshape(nHeight.value, nWidth.value, int(nBitCount.value/8))
        print("save to test.jpg code = %d" % (retValue))
        return image

    #bmpfile = "test.bmp"
    #pBmpfile = create_string_buffer(b'test.bmp', 64)
    #retValue = libKsj.KSJ_HelperSaveToBmp(pRawData, nWidth, nHeight, nBitCount, byref(pBmpfile))
    #print("save to bmp code = %d" % (retValue))
if __name__=="__main__":
    image1 = read(0)
    image2 = read(1)
    cv2.imwrite("test1.jpg", image1)
    cv2.imwrite("test2.jpg", image2)