#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import ctypes  # type: ignore
import sys
import unittest

import pylibopus.api
import pylibopus.api.encoder
import pylibopus.api.ctl

__author__ = 'Никита Кузнецов <self@svartalf.info>'
__copyright__ = 'Copyright (c) 2012, SvartalF'
__license__ = 'BSD 3-Clause License'


class EncoderTest(unittest.TestCase):
    """Encoder basic API tests

    From the `tests/test_opus_api.c`
    """

    def _test_unsupported_sample_rates(self):
        for cxx in range(0, 4):
            for ixx in range(-7, 96000 + 1):

                if ixx in (8000, 12000, 16000, 24000, 48000) and cxx in (1, 2):
                    continue

                if ixx == -5:
                    fsx = -8000
                elif ixx == -6:
                    fsx = sys.maxsize  # TODO: Must be an INT32_MAX
                elif ixx == -7:
                    fsx = -1 * (sys.maxsize - 1)  # TODO: Must be an INT32_MIN
                else:
                    fsx = ixx

                try:
                    pylibopus.api.encoder.create_state(
                        fsx, cxx, pylibopus.APPLICATION_VOIP)
                except pylibopus.OpusError as exc:
                    self.assertEqual(exc.code, pylibopus.BAD_ARG)

    def test_create(self):
        try:
            pylibopus.api.encoder.create_state(48000, 2, pylibopus.AUTO)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BAD_ARG)

        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_VOIP)
        pylibopus.api.encoder.destroy(enc)

        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_RESTRICTED_LOWDELAY)
        # TODO: rewrite that code
        # i = pylibopus.api.encoder.encoder_ctl(
        #     enc, pylibopus.api.ctl.get_lookahead)
        # if(err!=OPUS_OK || i<0 || i>32766)test_failed();
        pylibopus.api.encoder.destroy(enc)

        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)
        # TODO: rewrite that code
        # i = pylibopus.api.encoder.encoder_ctl(
        #     enc, pylibopus.api.ctl.get_lookahead)
        # err=opus_encoder_ctl(enc,OPUS_GET_LOOKAHEAD(&i));
        # if(err!=OPUS_OK || i<0 || i>32766)test_failed();
        pylibopus.api.encoder.destroy(enc)

    @classmethod
    def test_encode(cls):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)
        data = b'\x00' * ctypes.sizeof(ctypes.c_short) * 2 * 960
        pylibopus.api.encoder.encode(enc, data, 960, len(data))
        pylibopus.api.encoder.destroy(enc)

    @classmethod
    def test_encode_float(cls):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)
        data = b'\x00' * ctypes.sizeof(ctypes.c_float) * 2 * 960
        pylibopus.api.encoder.encode_float(enc, data, 960, len(data))
        pylibopus.api.encoder.destroy(enc)

    def test_unimplemented(self):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)
        try:
            pylibopus.api.encoder.encoder_ctl(enc, pylibopus.api.ctl.unimplemented)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.UNIMPLEMENTED)

        pylibopus.api.encoder.destroy(enc)

    def test_application(self):
        self.check_setget(
            pylibopus.api.ctl.set_application,
            pylibopus.api.ctl.get_application,
            (-1, pylibopus.AUTO),
            (pylibopus.APPLICATION_AUDIO,
             pylibopus.APPLICATION_RESTRICTED_LOWDELAY)
        )

    def test_bitrate(self):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)

        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bitrate, 1073741832)

        value = pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.get_bitrate)
        self.assertLess(value, 700000)
        self.assertGreater(value, 256000)

        pylibopus.api.encoder.destroy(enc)

        self.check_setget(
            pylibopus.api.ctl.set_bitrate,
            pylibopus.api.ctl.get_bitrate,
            (-12345, 0),
            (500, 256000)
        )

    def test_force_channels(self):
        self.check_setget(
            pylibopus.api.ctl.set_force_channels,
            pylibopus.api.ctl.get_force_channels,
            (-1, 3),
            (1, pylibopus.AUTO)
        )

    def test_bandwidth(self):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)

        # Set bandwidth
        ixx = -2
        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.encoder.encoder_ctl(
                enc, pylibopus.api.ctl.set_bandwidth, ixx)
        )

        ix1 = pylibopus.BANDWIDTH_FULLBAND + 1
        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.encoder.encoder_ctl(
                enc, pylibopus.api.ctl.set_bandwidth, ix1)
        )

        ix2 = pylibopus.BANDWIDTH_NARROWBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bandwidth, ix2)

        ix3 = pylibopus.BANDWIDTH_FULLBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bandwidth, ix3)

        ix4 = pylibopus.BANDWIDTH_WIDEBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bandwidth, ix4)

        ix5 = pylibopus.BANDWIDTH_MEDIUMBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bandwidth, ix5)

        # Get bandwidth
        value = pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.get_bandwidth)
        self.assertIn(
            value,
            (pylibopus.BANDWIDTH_FULLBAND,
             pylibopus.BANDWIDTH_MEDIUMBAND,
             pylibopus.BANDWIDTH_WIDEBAND,
             pylibopus.BANDWIDTH_NARROWBAND,
             pylibopus.AUTO)
        )

        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_bandwidth, pylibopus.AUTO)

        pylibopus.api.encoder.destroy(enc)

    def test_max_bandwidth(self):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)

        i = -2
        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.encoder.encoder_ctl(
                enc, pylibopus.api.ctl.set_max_bandwidth, i)
        )
        i = pylibopus.BANDWIDTH_FULLBAND + 1
        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.encoder.encoder_ctl(
                enc, pylibopus.api.ctl.set_max_bandwidth, i)
        )
        i = pylibopus.BANDWIDTH_NARROWBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_max_bandwidth, i)
        i = pylibopus.BANDWIDTH_FULLBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_max_bandwidth, i)
        i = pylibopus.BANDWIDTH_WIDEBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_max_bandwidth, i)
        i = pylibopus.BANDWIDTH_MEDIUMBAND
        pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.set_max_bandwidth, i)

        i = -12345
        value = pylibopus.api.encoder.encoder_ctl(
            enc, pylibopus.api.ctl.get_max_bandwidth)

        self.assertIn(
            value,
            (pylibopus.BANDWIDTH_FULLBAND,
             pylibopus.BANDWIDTH_MEDIUMBAND,
             pylibopus.BANDWIDTH_WIDEBAND,
             pylibopus.BANDWIDTH_NARROWBAND,
             pylibopus.AUTO)
        )

        pylibopus.api.encoder.destroy(enc)

    def test_dtx(self):
        self.check_setget(
            pylibopus.api.ctl.set_dtx, pylibopus.api.ctl.get_dtx, (-1, 2), (1, 0))

    def test_complexity(self):
        self.check_setget(
            pylibopus.api.ctl.set_complexity,
            pylibopus.api.ctl.get_complexity,
            (-1, 11),
            (0, 10)
        )

    def test_inband_fec(self):
        self.check_setget(
            pylibopus.api.ctl.set_inband_fec,
            pylibopus.api.ctl.get_inband_fec,
            (-1, 3),
            (1, 0)
        )

    def test_packet_loss_perc(self):
        self.check_setget(
            pylibopus.api.ctl.set_packet_loss_perc,
            pylibopus.api.ctl.get_packet_loss_perc,
            (-1, 101),
            (100, 0)
        )

    def test_vbr(self):
        self.check_setget(
            pylibopus.api.ctl.set_vbr, pylibopus.api.ctl.get_vbr, (-1, 2), (1, 0))

    def test_vbr_constraint(self):
        self.check_setget(
            pylibopus.api.ctl.set_vbr_constraint,
            pylibopus.api.ctl.get_vbr_constraint,
            (-1, 2),
            (1, 0)
        )

    def test_signal(self):
        self.check_setget(
            pylibopus.api.ctl.set_signal,
            pylibopus.api.ctl.get_signal,
            (-12345, 0x7FFFFFFF),
            (pylibopus.SIGNAL_MUSIC, pylibopus.AUTO)
        )

    def test_lsb_depth(self):
        self.check_setget(
            pylibopus.api.ctl.set_lsb_depth,
            pylibopus.api.ctl.get_lsb_depth,
            (7, 25),
            (16, 24)
        )

    def check_setget(self, v_set, v_get, bad, good):
        enc = pylibopus.api.encoder.create_state(
            48000, 2, pylibopus.APPLICATION_AUDIO)

        for value in bad:
            self.assertRaises(
                pylibopus.OpusError,
                lambda: pylibopus.api.encoder.encoder_ctl(enc, v_set, value)
            )

        for valuex in good:
            pylibopus.api.encoder.encoder_ctl(enc, v_set, valuex)
            result = pylibopus.api.encoder.encoder_ctl(enc, v_get)
            self.assertEqual(valuex, result)

        pylibopus.api.encoder.destroy(enc)
