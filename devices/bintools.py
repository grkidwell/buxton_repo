"""
Provide common bit manipulation functions

.. codeauthor:: Huan Nguyen
"""


def read_bit(register, mask, shift):
    """
    Perform bit reading operation

    :param register: The value of the register
    :param mask: The bitmask for the bits to be operated on
    :param shift: The shift distance for the bits
    :return: The bit values read
    """
    return (register & mask) >> shift


def set_bit(register, mask, shift, value):
    """
    Perform bit write operation

    :param register: The original value of the register
    :param mask: The bitmask for the bits to be operated on
    :param shift: The shift distance for the bits
    :param value: The new values for the bits
    :return: New register value with input value written
    """
    value = (value << shift) & mask
    register = register & ~mask
    return register | value


def to_bytes(value, size):
    """
    Return a byte array version of the integer

    :param value: Integer value to convert to bytes
    :param size: Expected size of output in bytes
    :return: Array of bytes representing the register
    """
    shift_reg = value
    byte_array = []
    for _ in range(size):
        byte_array.append(shift_reg & 0xff)
        shift_reg = shift_reg >> 8
    byte_array.reverse()
    return byte_array


def from_bytes(byte_array, size):
    """
    Take a byte array and convert it to int

    :param byte_array: Array of bytes to convert
    :param size: Expected size of output in bytes
    :return: Integer value of byte array
    """
    value = 0
    for cnt in range(size):
        value = value << 8
        value = value + byte_array[cnt]
    return value


def find_mask(key):
    """
    Given a __getitem__ index, return the bitmask needed to get/set the
    bits

    :param key: int or array slice representing the particular bits to be
        masked
    :return: int bitmask representing the input bits
    """
    mask = 0
    shift = 0
    if isinstance(key, int):
        mask = 1 << key
        shift = key
    elif isinstance(key, slice):
        start = key.start
        stop = key.stop
        if not isinstance(start, int) or not isinstance(stop, int):
            raise TypeError('Unexpected argument type, expecting int')
        if start > stop:
            start, stop = stop, start
        mask = (2 ** (stop - start) - 1) << start
        shift = start
    return mask, shift
