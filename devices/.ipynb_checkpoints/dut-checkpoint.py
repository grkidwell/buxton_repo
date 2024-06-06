import sys


# from devices.mockingbirdD as Mockingbird
# -----------------------------------------------------------------
#  This is the PMBus page number for each rail. 
#  This will probably never change, but in case
#  they do we define them here.   
# -----------------------------------------------------------------
from devices import mockingbirdD as Mockingbird

#  This class will write any PMBus command,
#  register on the device.  It will also read and
#  write bit-fields for both PMBus commands and
#  registers.  See example below for details.  
#  This class was generated from the regList.csv
#  degsign file.  All names and fields match the
#  HTML regList page. 
class DUT(Mockingbird.create):
    def __init__(self, address):
        Mockingbird.create.__init__(self, address)

    def example(self):
        # READING & WRITING REGISTERS
        # ------------------------------------------------

        # When an argument is passed in
        # a write operation will be done.
        # Below writes 0xD10 to pwrMode
        self.pwrMode(0xD10)

        # When no argument is passed in
        # a read operation will be done.
        # Below reads the current value
        # of pwrMode
        v = self.pwrMode()
        print("pwrMode = 0x%04X" % v)

        # READING & WRITTING BIT-FIELDS
        # ------------------------------------------------
        # You can also read and write
        # bit fields.

        # Same as above, When an argument
        # is passed in a write operation
        # will be done.
        # Below write the pwrMode bit field
        # vidDecayReg to 0
        self.pwrMode.vidDecayRej(0)

        # When no argument is passed in
        # a read operation will be done.
        v = self.pwrMode.vidDecayRej()
        print("pwrMode.vidDecayRej = 0x%04X" % v)

        # DMA
        # ------------------------------------------------

        # You can access PMBus registers as
        # commands or DMAs
        v = self.iocResp()
        print("iocResp = 0x%04X" % v)

        # You can numbers or strings
        v = self.dma(0xE05C);
        print("iocResp = 0x%04X" % v)

        v = self.dma('IOCRESP0');
        print("iocResp = 0x%04X" % v)

        # A DMA write will be done
        # when a second argument
        # is passed in.
        self.dma('IOCRESP0', v + 1);
        v = self.dma('IOCRESP0');
        print("iocResp = 0x%04X" % v)

        self.dma('IOCRESP0', v - 1);
        v = self.dma('IOCRESP0');
        print("iocResp = 0x%04X" % v)

        # REGISTER ATTRIBUTES
        # ------------------------------------------------
        # Each register knows the number of bits it is
        # and what interface it belongs to.
        print("firstPhAdcUcFltStat has %d bits" % self.firstPhAdcUcFltStat.bits)
        print("adcTest is part of the %s interface" % self.adcTest.interface)

    # -----------------------------------------------------------------
    # Reads or writes the output voltage for the rail.  If the value
    # is None (i.e. No argument was passed in) it will read the 
    # current voutCmd setting.  Otherwise it will set it.
    #
    # Example:
    #    v = vout(dut)  ; reads voutCmd
    #    vout(dut, 1.2) ; sets voutCmd to 1.2 by scaling a 1000
    # -----------------------------------------------------------------
    # TODO: Similar thing, syntax may have to change
    def vout(self, rail_page, value = None):
        self.page(rail_page)
        self.loopCfg.lockSvid(0)
        register = 'SVIDVIDSET%d' % rail_page
        if (value == None):
            value = self.dma(register) & 0xFF
        else:
            reg = self.dma(register) & 0xFF00
            reg += (value & 0xFF)
            self.dma(register, reg)

        return (value)

    def vout_old(self, rail_page, value = None):
        self.page(rail_page)
        self.loopCfg.lockSvid(3)
        if (value == None):
            value = self.voutCmd() / 1000.0
        else:
            self.voutCmd(int(value * 1000.0))

        return (value)

    # -----------------------------------------------------------------
    # Reads are writes the current pwoer state.  If value of ps is
    # none (i.e. No argument was passed in) it will read the
    # current power state.  Otherwise it will set it.
    # -----------------------------------------------------------------
    def power_state(self, rail_page, ps = None):
        self.page(rail_page)
        self.loopCfg.lockSvid(0)
        register = 'SVIDPSLP%d' % rail_page
        if (ps == None):
            ps = self.dma(register)
        else:
            self.dma(register, ps)

        return (ps)

    # -----------------------------------------------------------------
    # Use PMBus enable
    # -----------------------------------------------------------------
    def use_pmbus_enable(self, rail_page):
        self.page(rail_page)
        # Enable PMBus comands for both loops
        self.loopCfg.lockSvid(3)
        # Set for PMBus enable
        self.onOff(0x1A)

    # -----------------------------------------------------------------
    # Turn on the device
    # -----------------------------------------------------------------
    def enable(self, rail_page):
        self.page(rail_page)
        self.oper(0x88)

    # -----------------------------------------------------------------
    # Turn off the device
    # -----------------------------------------------------------------
    def disable(self, rail_page):
        self.page(rail_page)
        self.oper(0x48)

    # -----------------------------------------------------------------
    # Gets phase counts for the rails
    # -----------------------------------------------------------------
    def get_phase_count(self): #-> list[int]:
        return [3, 2, 1]
