#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
#

"""OpusLib Package."""

import ctypes  # type: ignore

from ctypes.util import find_library  # type: ignore


lib_location = None
libopus = None


def set_lib(path):
    new_lib_location = find_library(path)
    if new_lib_location is None:
        raise Exception(
            'Could not find Opus library. Make sure it is installed.')
    else:
        global lib_location, libopus
        lib_location = new_lib_location
        libopus = ctypes.CDLL(lib_location)


set_lib('opus')


c_int_pointer = ctypes.POINTER(ctypes.c_int)
c_int16_pointer = ctypes.POINTER(ctypes.c_int16)
c_float_pointer = ctypes.POINTER(ctypes.c_float)
c_ubyte_pointer = ctypes.POINTER(ctypes.c_ubyte)
