#!/usr/bin/env python

import devices.utility as utility

global utility

#============================================================
# 
#============================================================
class cPMBusCmd(object):
    def __init__(self, cmdNumber, cmdLength):
        self.command = cmdNumber
        self.length = cmdLength

    def Read(self, address):
        if (utility.IsDeviceOpen == False):
            utility.OpenDevice()
        
        if (self.length > 4):
            array = utility.PMBUS_Read_Block(address, self.command, self.length)
            shift = 0
            data = 0
            for byte in array[1]:
                data = data + (byte << shift)
                shift = shift + 8
                
        else:
            data = utility.PMBUS_Read(address, self.command, self.length)
        return (data)
        
    def Write(self, address, data):
        if (utility.IsDeviceOpen == False):
            utility.OpenDevice()
            
        utility.PMBUS_Write(address, self.command, self.length, data)

    def convertFromVout(self, data):
        y = (1.0 * data) / 2**13
        return (y)
        
    def convertToVout(self, decimal):
        y = int(decimal * 2**13)
        return (y)

    # Convert a LITERAL format (5-bit signed exponent , 11-bit signed mantissa)
    # to real number
    def convertFromLiteral(self, data):
        # Mantissa
        mantissa = 0.0
        x = data & 0x7FF
        if (x > 1023):
            mantissa = x - 2048.0
        else:
            mantissa = x 
            
        # Exponent
        x = data >> 11;
        if (x > 15):
            exponent = x - 32.0
        else:
            exponent = x

        y = mantissa * 2**exponent
        
        return (y)
        
    def convertToLiteral(self, decimal):
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
        
#============================================================
# 
#============================================================
class cPMBusNoDataCmd(cPMBusCmd):
    def __init__(self, cmdNumber):
        cPMBusCmd.__init__(self, cmdNumber, 0)

    def Write(self, address):
        if (utility.IsDeviceOpen == False):
            utility.OpenDevice()
            
        utility.PMBUS_Write(address, self.command, self.length, 0)
        
#============================================================
# 
#============================================================
class cPMBusByteCmd(cPMBusCmd):
    def __init__(self, cmdNumber):
        cPMBusCmd.__init__(self, cmdNumber, 1)
        
#============================================================
# 
#============================================================
class cPMBusIntCmd(cPMBusCmd):
    def __init__(self, cmdNumber):
        cPMBusCmd.__init__(self, cmdNumber, 2)

#============================================================
# 
#============================================================
class cPMBusLongCmd(cPMBusCmd):
    def __init__(self, cmdNumber):
        cPMBusCmd.__init__(self, cmdNumber, 4)

#============================================================
# 
#============================================================
class cPMBusBlockCmd(cPMBusCmd):
    def __init__(self, cmdNumber, Size):
        cPMBusCmd.__init__(self, cmdNumber, Size)

#============================================================
# 
#============================================================
class cPMBusStringCmd(cPMBusCmd):
    def __init__(self, cmdNumber, length):
        cPMBusCmd.__init__(self, cmdNumber, length)

    def Read(self, address):
        text = ''
        data = cPMBusCmd.Read(self, address)
        if (isinstance(data, int)):
            text = str(data)
        else:
            for d in data[1]:
                text = text + chr(d)
        
        return (text)
            
#============================================================
# 
#============================================================
class cPMBusVoltageCmd(cPMBusIntCmd):
    def __init__(self, cmdNumber):
        cPMBusIntCmd.__init__(self, cmdNumber)
        voltage = 0.0

    def Read(self, address):
        data = cPMBusIntCmd.Read(self, address)
        self.voltage = self.convertFromVout(data)
        return (self.voltage)

    def Write(self, address, volt):
        self.voltage = volt
        data = self.convertToVout(self.voltage)
        cPMBusCmd.Write(self, address, data)
        
#============================================================
# 
#============================================================
class cPMBusLiteralCmd(cPMBusIntCmd):
    def __init__(self, cmdNumber):
        cPMBusIntCmd.__init__(self, cmdNumber)
        value = 0.0

    def Read(self, address):
        data = cPMBusIntCmd.Read(self, address)
        self.value = self.convertFromLiteral(data)
        #print("[PMBusLiteralCmd] Read %f [%s]" % (self.value, hex(data)))
        return (self.value)

    def Write(self, address, value):
        self.value = value
        data = self.convertToLiteral(self.value)
        cPMBusCmd.Write(self, address, data)
        #print("[PMBusLiteralCmd] Writting %f [%s]" % (self.value, hex(data)))
  
class cPMBusDMAReadCmd(cPMBusCmd):
    def __init__(self):
        cPMBusCmd.__init__(self, 0xEC, 3)
            
    def Read(self, address):
        if (utility.IsDeviceOpen == False):
            print("Opening Device")
            utility.OpenDevice()
        
        print("Cmd %X" % self.command)
        print("Len %X" % self.length)
        data = utility.PMBUS_Read(address, self.command, self.length)
        return (data)
    
  
