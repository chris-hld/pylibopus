#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,too-few-public-methods
#

"""
CTypes mapping between libopus functions and Python.
"""

import array
import ctypes  # type: ignore
import typing

import pylibopus
import pylibopus.api

__author__ = 'Chris Hold>'
__copyright__ = 'Copyright (c) 2024, Chris Hold'
__license__ = 'BSD 3-Clause License'


class ProjectionDecoder(ctypes.Structure):
    """Opus multi-stream decoder state.
    This contains the complete state of an Opus decoder.
    """
    pass


ProjectionDecoderPointer = ctypes.POINTER(ProjectionDecoder)


libopus_get_size = pylibopus.api.libopus.opus_projection_decoder_get_size
libopus_get_size.argtypes = (ctypes.c_int, ctypes.c_int)
libopus_get_size.restype = ctypes.c_int
libopus_get_size.__doc__ = 'Gets the size of an OpusProjectionDecoder structure'


libopus_create = pylibopus.api.libopus.opus_projection_decoder_create
libopus_create.argtypes = (
    ctypes.c_int,  # fs
    ctypes.c_int,  # channels
    ctypes.c_int,  # streams
    ctypes.c_int,  # coupled streams
    pylibopus.api.c_ubyte_pointer,  # demixing_matrix
    ctypes.c_int,  # demixing_matrix_size
    pylibopus.api.c_int_pointer  # error
)
libopus_create.restype = ProjectionDecoderPointer


def create_state(fs: int, channels: int, streams: int, coupled_streams: int,
                 demixing_matrix: list) -> ctypes.Structure:
    """
    Allocates and initializes a decoder state.

    `fs` must be one of 8000, 12000, 16000, 24000, or 48000.

    :param fs: Sample rate to decode at (Hz).
    """
    result_code = ctypes.c_int()
    _udemixing_matrix = (ctypes.c_ubyte * len(demixing_matrix))(*demixing_matrix)
    demixing_matrix_size = ctypes.c_int(len(demixing_matrix))

    decoder_state = libopus_create(
        fs,
        channels,
        streams,
        coupled_streams,
        _udemixing_matrix,
        demixing_matrix_size,
        ctypes.byref(result_code)
    )

    if result_code.value != pylibopus.OK:
        raise pylibopus.exceptions.OpusError(result_code.value)

    return decoder_state


libopus_decode = pylibopus.api.libopus.opus_projection_decode
libopus_decode.argtypes = (
    ProjectionDecoderPointer,
    ctypes.c_char_p,
    ctypes.c_int32,
    pylibopus.api.c_int16_pointer,
    ctypes.c_int,
    ctypes.c_int
)
libopus_decode.restype = ctypes.c_int


# FIXME: Remove typing.Any once we have a stub for ctypes
def decode(  # pylint: disable=too-many-arguments
        decoder_state: ctypes.Structure,
        opus_data: bytes,
        length: int,
        frame_size: int,
        decode_fec: bool,
        channels: int = 2
) -> typing.Union[bytes, typing.Any]:
    """
    Decode an Opus Frame to PCM.

    Unlike the `opus_decode` function , this function takes an additional
    parameter `channels`, which indicates the number of channels in the frame.
    """
    _decode_fec = int(decode_fec)
    result = 0

    pcm_size = frame_size * channels * ctypes.sizeof(ctypes.c_int16)
    pcm = (ctypes.c_int16 * pcm_size)()
    pcm_pointer = ctypes.cast(pcm, pylibopus.api.c_int16_pointer)

    result = libopus_decode(
        decoder_state,
        opus_data,
        length,
        pcm_pointer,
        frame_size,
        _decode_fec
    )

    if result < 0:
        raise pylibopus.exceptions.OpusError(result)

    return array.array('h', pcm_pointer[:result * channels]).tobytes()


libopus_decode_float = pylibopus.api.libopus.opus_projection_decode_float
libopus_decode_float.argtypes = (
    ProjectionDecoderPointer,
    ctypes.c_char_p,
    ctypes.c_int32,
    pylibopus.api.c_float_pointer,
    ctypes.c_int,
    ctypes.c_int
)
libopus_decode_float.restype = ctypes.c_int


# FIXME: Remove typing.Any once we have a stub for ctypes
def decode_float(  # pylint: disable=too-many-arguments
        decoder_state: ctypes.Structure,
        opus_data: bytes,
        length: int,
        frame_size: int,
        decode_fec: bool,
        channels: int = 2
) -> typing.Union[bytes, typing.Any]:
    """
    Decode an Opus Frame.

    Unlike the `opus_decode` function , this function takes an additional
    parameter `channels`, which indicates the number of channels in the frame.
    """
    _decode_fec = int(decode_fec)

    pcm_size = frame_size * channels * ctypes.sizeof(ctypes.c_float)
    pcm = (ctypes.c_float * pcm_size)()
    pcm_pointer = ctypes.cast(pcm, pylibopus.api.c_float_pointer)

    result = libopus_decode_float(
        decoder_state,
        opus_data,
        length,
        pcm_pointer,
        frame_size,
        _decode_fec
    )

    if result < 0:
        raise pylibopus.exceptions.OpusError(result)

    return array.array('f', pcm[:result * channels]).tobytes()


libopus_ctl = pylibopus.api.libopus.opus_projection_decoder_ctl
libopus_ctl.argtypes = [ProjectionDecoderPointer, ctypes.c_int,]  # variadic
libopus_ctl.restype = ctypes.c_int


# FIXME: Remove typing.Any once we have a stub for ctypes
def decoder_ctl(
        decoder_state: ctypes.Structure,
        request,
        value=None
) -> typing.Union[int, typing.Any]:
    if value is not None:
        return request(libopus_ctl, decoder_state, value)
    return request(libopus_ctl, decoder_state)


destroy = pylibopus.api.libopus.opus_projection_decoder_destroy
destroy.argtypes = (ProjectionDecoderPointer,)
destroy.restype = None
destroy.__doc__ = 'Frees an OpusProjectionDecoder allocated by opus_projection_decoder_create()'
