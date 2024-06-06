'''
Created on Mar 12, 2014

@author: dbeck
'''
import sys, os
import time
try:
    import pyvisa as visa # Import DNSPython
    visa_available = True
except ImportError:
    visa_available = False

#global rtlDirectory
#rtlDirectory = 'D:\\caddo\\fpga\\caddoFullLoop\\design\\i2cInterface\\'


#print = libc.print

#globals
#PmbusAddress = 0x20

from .dongle import IntersilDongle
global dongle
IsDeviceOpen = False

def OpenDevice() :
    global dongle
    global IsDeviceOpen
    dongle = IntersilDongle.get_dongle()
    IsDeviceOpen = True
    
def DMA_Write(address,data) :
    global dongle
    dongle.write(PmbusAddress,0xEE,2,address,mode = 'int')
    #time.sleep(0.1)
    dongle.write(PmbusAddress, 0xEC, 1,data,mode = 'int')
    
def DMA_Read(devAddress, address) :
    global dongle
    dongle.write(devAddress,0xEE,2,address,mode = 'int')
    #readback = (dongle.read(devAddress, 0xEC, 1,mode = 'int'))
    readback = (dongle.read(devAddress, 0xEC, 3,mode = 'bytes'))
    print(readback)
    return readback[1][2]

def DMA_Write_Sequential(address,data,size) :
    global dongle
    dongle.write(PmbusAddress,0xEE,2,address,mode = 'int')
    #time.sleep(0.1)
    dongle.write(PmbusAddress, 0xED, size,data)

def DMA_Read_Sequential(devAddress, address,size) :
    global dongle
    dongle.write(devAddress,0xEE,2,address,mode = 'int')
    readback = (dongle.read(devAddress, 0xED, size))
    return readback

def DMA_Address(address) :
    global dongle
    global PmbusAddress
    dongle.write(PmbusAddress,0xEE,2,address,mode = 'int')

def CloseDevice() :
    global dongle
    global IsDeviceOpen
    dongle.close()
    IsDeviceOpen = False

def PMBUS_Read(address, command, length) :
    global dongle
    if (length > 4):
        readback = (dongle.read(address, command, 'block',mode = 'bytes'))
        out = 0
        i = 0
        for data in readback[1]:
            out = (data << (8 * i)) + out
            i += 1
    else:
        readback = (dongle.read(address, command, length, mode = 'int'))
        out = readback[1]
    return out

def PMBUS_Read_Block(address, command, length) :
    global dongle
    readback = (dongle.read(address, command, 'block',mode = 'bytes'))
    return(readback)
    
def PMBUS_Write(address, command, length, data) :
    global dongle
    if (length > 4):
        bytes = []
        i = 0
        while (i<length):
            bytes.append(data % 256)
            data = int(data / 256)
            i += 1
        dongle.write(address,command,'block',bytes,mode = 'bytes')
    else:
        dongle.write(address,command,length,data,mode = 'int')

def addressScan():
    global dongle
    addressList = []
    address = 0
    OpenDevice()
    while (address < 0x80):
        readback = dongle.read(address, 0xEE, 2,mode = 'int')
        if (readback[0] == 0) and (readback[1] != 0xFFFF):
            addressList.append(address)
        address += 1
    CloseDevice()
    return(addressList)

def signExtend(x,N):
	if (x >= (1<<(N-1))):
		return (x - (1<<N))
	else:
		return x
        
# Convert a LITERAL format (5-bit signed exponenet , 11-bit signed mantissa)
# to real number
def convertFromLiteral(data):
    # Mantissa
    mantissa = data & 0x7FF
    mantissa = signExtend(mantissa,11)
    # Exponent
    exponent = data >> 11;
    exponent = signExtend(exponent,5)

    y = mantissa * 2**exponent
    # if (exponent < 0):
        # exponent = exponent * -1
        # y = (1.0*mantissa) / (1.0*(1 << exponent))
    # else:
        # y = (1.0*mantissa) * (1.0*(1 << exponent))
    
    return (y)
    
def convertFromVout(data):
    y = (1.0 * data) / 2**13
    return (y)
    
def convertToVout(decimal):
    y = int(decimal * 2**13)
    return (y)

def convertToLiteral(decimal):
    # Literal Conversion:  s5E,s11M
    
    mag = abs(decimal)
    if (decimal < 0):
        sign = -1
    else:
        sign = 1
    
    exponent = -16
    mantissa = (1 << 10)
    while (mantissa > (1 << 10)-1) and (exponent < 15):
        mantissa = int(mag / (2.0 ** exponent))
        #print "literal debug",mantissa,exponent
        exponent += 1

    exponent -= 1

    if (sign == -1):
        mantissa = -1 * mantissa;

    #print "Literal M,E=",mantissa,exponent

    # convert to signed hex
    width = 5
    var = exponent
    if (exponent < 0):
        exponent = 2**width + exponent
        
    # convert to signed hex
    width = 11
    var = mantissa
    if (mantissa < 0):
        mantissa = 2**width + mantissa

    literal = mantissa | (exponent << 11)
    return (literal)

