#
##############################################
#
#   Driver for Sorenson MM2 electronic load
#
#   author: G.Kidwell
#
##############################################

import pyvisa as visa
rm = visa.ResourceManager("C:\\Windows\\System32\\visa32.dll")
rm.list_resources()

class SorensonMM2:
    def __init__(self,visa_rm=rm,gpio_ch=8,active_ch=1):
        self.rm = visa_rm
        self.gpioch = gpio_ch
        self.device = self.rm.open_resource('GPIB0::'+str(gpio_ch)+'::INSTR')
        self.ch = active_ch
        self.device.write('CHAN'+' '+str(self.ch))
        self.device.write('ACT ON')
        self.device.write('MODE CCH')
        
    def set_value(self,current):
        self.device.write('CHAN'+' '+str(self.ch))
        self.device.write('ACT ON')
        self.device.write('CURR:STAT:L'+str(1)+' '+str(current))
        
    def on(self):
        self.device.write('CHAN'+' '+str(self.ch))
        self.device.write('ACT ON')
        self.device.write('LOAD ON')
        
    def off(self):
        self.device.write('CHAN'+' '+str(self.ch))
        self.device.write('ACT ON')
        self.device.write('LOAD OFF')
        
    def meas(self):
        self.device.write('CHAN'+' '+str(self.ch))
        self.device.write('ACT ON')
        return float(self.device.query('MEAS:CURR?').strip('\n'))

    def disconnect(self):
        self.device.write('CHAN'+' '+str(self.ch))
        #self.device.write('ACT ON')
        self.device.write('ACT OFF')
        
class Kikusui:
    def __init__(self,visa_rm=rm,address=str):
        self.rm = visa_rm
        self.device = self.rm.open_resource(address)
        self.device.write('SOURce:FUNCtion:MODE CC')
    
    def set_value(self,current_A):
        self.device.write(f"SOURce:CURRent:LEVel:IMMediate:AMPLitude {current_A}")
        
    def on(self):
        self.device.write('OUTPut:STATe 1')
        
    def off(self):
        self.device.write('OUTPut:STATe 0')
     
    def meas(self) -> float:
        return float(self.device.query('MEASure:CURRent:DC?').strip())
    
    def disconnect(self):
        pass