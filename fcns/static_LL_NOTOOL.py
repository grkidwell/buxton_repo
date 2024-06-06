# ------------------------------------------------------------------------------------
# ----Author - G. Kidwell
# 
# 
# ---Modified from static_LL.py to work without the VTT tool and instead query
# imon ....and potential vsense.....values from the controller
# 
#
#--------------------------------------------------------------------------------------

import os, sys, time #,clr
import numpy as np
from instr.gpib_equip import SorensonMM2, Kikusui
from register_operators import read_reg
from devices.dut_buxton import *

import openpyxl
from openpyxl import load_workbook,Workbook


import testplan_specs


def setup_initial_voltage(testrail,testvoltage):
    pass


class Loadline:
    def __init__(self,dut,testrail,powerstate,testcurrents,iccmax,loadhw): #raildata
        #self.load1 = SorensonMM2(active_ch=1); self.load2 = SorensonMM2(active_ch=3)
        #self.load3 = Kikusui(address='USB0::0x0B3E::0x1042::CQ005385::INSTR')
        self.load1max=25;                      
        self.dut = dut
        self.testrail=testrail
        self.railpage =  {'VCCCORE':0,'VCCGT':1,'VCCSA':2}[self.testrail]
        self.ps=int(powerstate);               self.testcurrents=testcurrents
        self.iccmax=iccmax;                    self.voffset_cal = 0.000
        self.loadhw = loadhw
    
    def scale_imon(self,imon_hex_value):
        return np.round(int(imon_hex_value,16)/0xff*self.iccmax,3)

   
    def read_imon_dut(self):
        # dma_cmd = 'svidiout'+str(self.railpage)
        # dimon = self.dut.dma(dma_cmd)
        imonreg_sa = 0x50
        dimon = read_reg(self.dut.addr,imonreg_sa)
        return f'{dimon}'

    def avg_dimon(self):
        return f'{int(sum([int(self.read_imon_dut(),16) for count in range(3)])/3):x}' 
    
    def read_phase_cnt(self):
        phase_num_reg = 0x5C
        
        nphase = int(read_reg(self.dut.addr,phase_num_reg),16)
        return nphase

    def load_kikusui(self, testcurrent):
        self.load = {'load1':Kikusui(address='TCPIP0::132.158.231.12::INSTR')}#'USB0::0x0B3E::0x1042::CQ005385::INSTR')}
        kikload = self.load['load1']
        kikload.set_value(testcurrent); kikload.on(); time.sleep(1)
        return np.round(kikload.meas(),3)
        
    def load_sorensen(self,testcurrent):
        def meas_load(current,loadn):
            loadn.set_value(current); loadn.on(); time.sleep(1)
            return np.round(loadn.meas(),3)
        
        self.load = {'load1':SorensonMM2(active_ch=1),
                     'load2':SorensonMM2(active_ch=3)
                    }
        load2_pct=0.5*(testcurrent>self.load1max) #/100 
        total_load=meas_load(testcurrent*(1-load2_pct),self.load['load1'])+ \
                   (meas_load(testcurrent*load2_pct,self.load['load2']) if load2_pct else 0)
        return np.round(total_load,3)


    def set_ps(self):
        #self.dut.power_state(self.railpage,self.ps)
        time.sleep(0.25)

    def take_data(self):
        self.set_ps()
        def get_values_and_print(current):
            loadhw_dict = {'kikusui': self.load_kikusui,
                           'sorensen':self.load_sorensen}
            load=loadhw_dict[self.loadhw](current) #{'sorensen':self.load_sorensen(current),
                  #'vtt'     :self.load_vtt(current)}[self.loadhw]
            time.sleep(1)
            #vout,vpp,vpos_ripple,vneg_ripple = measure_vout_ripple(self.testrail)
            # dd = {'load'  : load,            'vsense': vout+self.voffset_cal,
            #       'ripple': vpp,             'vpos_ripple':vpos_ripple,
            #       'vneg_ripple':vneg_ripple, 'dimon' : self.read_imon_dut()} #vector()}
            dd = {'load':load,'dimon':self.read_imon_dut(),'nphase':self.read_phase_cnt()}
            dd['imon'] = self.scale_imon(dd['dimon'])
            #print(f"{dd['load']}\t{dd['vsense']}\t{dd['ripple']}\t{dd['dimon']}\t{dd['imon']}")
            print(f"{dd['load']}\t{dd['dimon']}\t{dd['imon']}\t{dd['nphase']}")
            return dd
        self.dataset = [get_values_and_print(current) for current in self.testcurrents]
        
        for loadn in self.load.keys():
            self.load[loadn].off()
            self.load[loadn].disconnect()
            
        #self.load1.off(); self.load2.off(); self.load1.disconnect(); self.load2.disconnect()


def setup_and_take_data(pmbaddr:int,family:str,power:str,test_rail:str,pstate:int,loadhw:str):
    dut: DUT = DUT(pmbaddr)
    ps = str(pstate)
#    rail_data     = define_rail_data(test_rail)
#    test_voltage  = testplan_specs.test_voltage[ps]
    icc_max       = testplan_specs.current_specs[family][power]['icc_max'][test_rail]
    tdc           = testplan_specs.current_specs[family][power]['tdc'][test_rail]
    test_currents = testplan_specs.test_currents(tdc)[ps]
                        
#    setup_initial_voltage(test_rail,test_voltage)
    
    loadline_dataset = Loadline(dut,test_rail,ps,test_currents,icc_max,loadhw)

    print("##################################")
    print("----------------------------------")
    print(f"    IMON AND PHASECOUNT  AT PS = {ps}    ")
    print("----------------------------------")
    print("##################################")
    print("")
    print("Begining Test")
    print("")
#    print(f"If max load > {loadline_dataset.load1max}A connect 2nd load to evalboard")           
    print("")
    print('...............................')
    print('load\tdIMON\tIMON\tnPHASE')
    print('...............................')

    loadline_dataset.take_data()
    #reset_vtt_tool(test_rail)
    
    print("-------------------------------")
    print("")
    print("Test complete.")
    
    return loadline_dataset.dataset
