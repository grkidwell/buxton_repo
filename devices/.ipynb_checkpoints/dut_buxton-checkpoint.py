#import sys

from register_operators import read_reg

class DUT:
    def __init__(self,address):
        self.addr = address
        self.imon_addr_dict = {'VCCSA':0x50}
        
    def imon(self,rail):
        imon_addr = self.imon_addr_dict[rail]
        return read_reg(self.addr,imon_addr)