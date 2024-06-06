"""
Module for Intersil USB to I2C dongle
"""
import sys
from .bintools import to_bytes
import pywinusb.hid as hid
import math
from collections import OrderedDict
from weakref import WeakValueDictionary

Enable_PEC = False

class IntersilDongle(object):
    """
    Intersil dongle factory. Should be used to connect to the dongle wrapper
    """

    # Intersil's USB vendor ID
    VENDOR_ID = 0x09aa
    device_filter = hid.HidDeviceFilter

    _dongle_cache = WeakValueDictionary()

    def __new__(cls, device):
        if device.device_path in cls._dongle_cache:
            return cls._dongle_cache[device.device_path]
        device_wrapper = _IntersilDongleWrapper(device)
        cls._dongle_cache[device.device_path] = device_wrapper
        return device_wrapper

    @classmethod
    def get_devices(cls):
        """
        Return a dictionary of dongles attached to the host

        :return: OrderedDict with USB path for key and HID device as value
        """
        device_list = cls.device_filter(
            vendor_id=cls.VENDOR_ID).get_devices()
        return OrderedDict(
            [(device.device_path, device) for device in device_list]
            )

    @classmethod
    def get_dongle(cls):
        """
        Sometimes you just don't care where the dongle is, just find me one

        :return: Instantiated IntersilDongle
        """
        device_list = cls.device_filter(
            vendor_id=cls.VENDOR_ID).get_devices()
        if (len(device_list) == 0):
            print('*******************************************')
            print('Cannot Access USB dongle.')
            print('Please close applications using the dongle.')
            print('*******************************************')
            sys.exit(1)
        else:
            return cls(device_list[0])

    @classmethod
    def close_connections(cls):
        """
        Close all the connections so python can terminate
        """
        for wrapper in cls._dongle_cache.values():
            wrapper.close()

    @classmethod
    def remove(cls, path):
        """
        Remove dongle_test from opened device cache

        :param path: HID device path to remove from cache
        """
        del cls._dongle_cache[path]


class _IntersilDongleWrapper(object):
    """
    Intersil dongle_test control class. Class should not be used directly
    but proxied through a I2C instance
    """

    def __init__(self, device):
        super(_IntersilDongleWrapper, self).__init__()
        self.device = device
        self.device.open()
        self._input_report = self.device.find_input_reports()[0]
        self._output_report = self.device.find_output_reports()[0]
        self._target = next(iter(self._output_report.keys()))
        self.s_alert = True
        self._setup_i2c()

    def __str__(self):
        return '<{0} at {1:#8x}>'.format(self.__class__.__name__, id(self))

    @property
    def device_path(self):
        """
        :return: The device path of the dongle_test object it wraps
        """
        return self.device.device_path

    def read(self, address, command, size, **kwargs):
        global Enable_PEC
        """
        Perform I2C read

        :param address: DUT I2C address
        :param command: I2C command to send to device
        :param size: Size in bytes of the data to be read
        :keyword mode: If mode is set to 'int' then data will be returned as a
            single integer, if mode is not set, returns array of bytes
        :return: Tuple containing (status code, read data)
        """
        read_address = ((address & 0x7f) << 1) + 1
        if size == 'block' or size == 'dma':
            self._dev_write(read_address, command, 0)
        else:
            # If PEC is enabled we need to read one more byte
            # from the slave which will be a CRC for error
            # checking.
            # TODO:  I need to add PEC to the writes as well
            if (Enable_PEC == False):
                self._dev_write(read_address, command, size)
            else:
                self._dev_write(read_address, command, size+1)
        status, result = self._dev_read()
        
        if status == -1:
            byte_array = []
        if size == 1:
            byte_array = [result[2]]
        elif size == 2:
            byte_array = result[3:1:-1]
        elif size == 4:
            byte_array = result[5:1:-1]
        elif size == 'block':
            result_size = result[2]
            byte_array = result[3:3 + result_size]
        else:
            byte_array = result[2:2 + size]
        mode = kwargs.get('mode', 'bytes')
        if mode == 'int':
            value = 0
            for byte in byte_array:
                value = value << 8
                value = value + byte
        else:
            value = byte_array
            
        return (status, value)

    def write(self, address, command, size, data, **kwargs):
        """
        Perform I2C write

        :param address: DUT I2C address
        :param command: I2C command to send to device
        :param size: size in bytes of data to be written
        :param data: Data to be written in the format of a list of bytes
        :keyword mode: If mode is set to 'int' then input data is single
            integer, if mode is not set, data must be an array of bytes
        :return: Write status code
        """
        write_address = (address & 0x7f) << 1
        mode = kwargs.get('mode', 'bytes')
        if mode == 'bytes':
            byte_array = data
            if size == 2:
                byte_array.reverse()
        elif mode == 'int':
            if isinstance(size, int):
                int_size = size
            else:
                if data == 0:
                    int_size = 1
                else:
                    int_size = int(math.log(data, 256)) + 1
            byte_array = to_bytes(data, int_size)
        self._dev_write(write_address, command, size, byte_array)
        return self._dev_read()[0]

    def close(self):
        """
        Close the dongle_test interface
        """
        self.device.close()
        # pylint: disable=protected-access
        if self.device.device_path in IntersilDongle._dongle_cache:
            IntersilDongle.remove(self.device.device_path)
        return

    def _setup_i2c(self):
        """
        Perform dongle_test initialization
        """
        write_buffer = [0] * 63
        write_buffer[0] = 4  # Value for I2C config
        write_buffer[1] = 0  # Config write
        write_buffer[2] = 1  # Repeated start
        write_buffer[3] = 0  # EXTHOLD Low
        write_buffer[4] = 0  # Don't toggle SCL if SDA stuck low

        self._output_report[self._target] = write_buffer
        self._output_report.send()

    def _dev_write(self, address, command, size, data=None):
        """
        Perform the dongle_test write
        """
        if size == 'block':
            buf_size = len(data) + 1
        else:
            buf_size = size

        write_buffer = [0] * 63
        write_buffer[0] = 6  # Value for I2C transaction
        write_buffer[1] = address
        write_buffer[2] = buf_size
        write_buffer[3] = 1
        write_buffer[4] = command

        if data:
            if size == 1:
                write_buffer[5] = data[0]
            elif size == 2:
                write_buffer[5] = data[1]
                write_buffer[6] = data[0]
            elif size == 4:
                write_buffer[5] = data[3]
                write_buffer[6] = data[2]
                write_buffer[7] = data[1]
                write_buffer[8] = data[0]
            else:
                if size == 'block':
                    data.insert(0, buf_size - 1)
                for index in range(buf_size):
                    write_buffer[5 + index] = data[index]

        self._output_report[self._target] = write_buffer
        self._output_report.send()

    def _dev_read(self):
        """
        Perform the dongle_test read
        """
        read_buffer = self._input_report.get()
        
        if (read_buffer[1] & 0x80) == 0x00:
            self.s_alert = True
        else:
            self.s_alert = False
        if (read_buffer[1] & 0x01) == 0x01:
            status = -1
        else:
            status = 0
        return status, read_buffer
