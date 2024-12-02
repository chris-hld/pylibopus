#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

import sys
import unittest

import pylibopus.api
import pylibopus.api.decoder
import pylibopus.api.ctl

__author__ = 'Никита Кузнецов <self@svartalf.info>'
__copyright__ = 'Copyright (c) 2012, SvartalF'
__license__ = 'BSD 3-Clause License'


class DecoderTest(unittest.TestCase):
    """Decoder basic API tests

    From the `tests/test_opus_api.c`
    """

    def test_get_size(self):
        """Invalid configurations which should fail"""

        for csx in range(4):
            ixx = pylibopus.api.decoder.libopus_get_size(csx)
            if csx in (1, 2):
                self.assertFalse(1 << 16 < ixx <= 2048)
            else:
                self.assertEqual(ixx, 0)

    def _test_unsupported_sample_rates(self):
        """
        Unsupported sample rates

        TODO: make the same test with a opus_decoder_init() function
        """
        for csx in range(4):
            for ixx in range(-7, 96000):
                if ixx in (8000, 12000, 16000, 24000, 48000) and csx in (1, 2):
                    continue

                if ixx == -5:
                    fsx = -8000
                elif ixx == -6:
                    fsx = sys.maxsize  # TODO: should be a INT32_MAX
                elif ixx == -7:
                    fsx = -1 * (sys.maxsize - 1)  # Emulation of the INT32_MIN
                else:
                    fsx = ixx

                try:
                    dec = pylibopus.api.decoder.create_state(fsx, csx)
                except pylibopus.OpusError as exc:
                    self.assertEqual(exc.code, pylibopus.BAD_ARG)
                else:
                    pylibopus.api.decoder.destroy(dec)

    @classmethod
    def test_create(cls):
        try:
            dec = pylibopus.api.decoder.create_state(48000, 2)
        except pylibopus.OpusError:
            raise AssertionError()
        else:
            pylibopus.api.decoder.destroy(dec)

            # TODO: rewrite this code
        # VG_CHECK(dec,opus_decoder_get_size(2));

    @classmethod
    def test_get_final_range(cls):
        dec = pylibopus.api.decoder.create_state(48000, 2)
        pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_final_range)
        pylibopus.api.decoder.destroy(dec)

    def test_unimplemented(self):
        dec = pylibopus.api.decoder.create_state(48000, 2)

        try:
            pylibopus.api.decoder.decoder_ctl(
                dec, pylibopus.api.ctl.unimplemented)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.UNIMPLEMENTED)

        pylibopus.api.decoder.destroy(dec)

    def test_get_bandwidth(self):
        dec = pylibopus.api.decoder.create_state(48000, 2)
        value = pylibopus.api.decoder.decoder_ctl(
            dec, pylibopus.api.ctl.get_bandwidth)
        self.assertEqual(value, 0)
        pylibopus.api.decoder.destroy(dec)

    def test_get_pitch(self):
        dec = pylibopus.api.decoder.create_state(48000, 2)

        i = pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        packet = bytes([252, 0, 0])
        pylibopus.api.decoder.decode(dec, packet, 3, 960, False)
        i = pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        packet = bytes([1, 0, 0])
        pylibopus.api.decoder.decode(dec, packet, 3, 960, False)
        i = pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_pitch)
        self.assertIn(i, (-1, 0))

        pylibopus.api.decoder.destroy(dec)

    def test_gain(self):
        dec = pylibopus.api.decoder.create_state(48000, 2)

        i = pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_gain)
        self.assertEqual(i, 0)

        try:
            pylibopus.api.decoder.decoder_ctl(
                dec, pylibopus.api.ctl.set_gain, -32769)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BAD_ARG)

        try:
            pylibopus.api.decoder.decoder_ctl(
                dec, pylibopus.api.ctl.set_gain, 32768)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BAD_ARG)

        pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.set_gain, -15)
        i = pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.get_gain)
        self.assertEqual(i, -15)

        pylibopus.api.decoder.destroy(dec)

    @classmethod
    def test_reset_state(cls):
        dec = pylibopus.api.decoder.create_state(48000, 2)
        pylibopus.api.decoder.decoder_ctl(dec, pylibopus.api.ctl.reset_state)
        pylibopus.api.decoder.destroy(dec)

    def test_get_nb_samples(self):
        """opus_decoder_get_nb_samples()"""

        dec = pylibopus.api.decoder.create_state(48000, 2)

        self.assertEqual(
            480, pylibopus.api.decoder.get_nb_samples(dec, bytes([0]), 1))

        packet = bytes()
        for xxc in ((63 << 2) | 3, 63):
            packet += bytes([xxc])

        # TODO: check for exception code
        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.decoder.get_nb_samples(dec, packet, 2)
        )

        pylibopus.api.decoder.destroy(dec)

    def test_packet_get_nb_frames(self):
        """opus_packet_get_nb_frames()"""

        packet = bytes()
        for xxc in ((63 << 2) | 3, 63):
            packet += bytes([xxc])

        self.assertRaises(
            pylibopus.OpusError,
            lambda: pylibopus.api.decoder.packet_get_nb_frames(packet, 0)
        )

        l1res = (1, 2, 2, pylibopus.INVALID_PACKET)

        for ixc in range(0, 256):
            packet = bytes([ixc])
            expected_result = l1res[ixc & 3]

            try:
                self.assertEqual(
                    expected_result,
                    pylibopus.api.decoder.packet_get_nb_frames(packet, 1)
                )
            except pylibopus.OpusError as exc:
                if exc.code == expected_result:
                    continue

            for jxc in range(0, 256):
                packet = bytes([ixc, jxc])

                self.assertEqual(
                    expected_result if expected_result != 3 else (packet[1] & 63),  # NOQA
                    pylibopus.api.decoder.packet_get_nb_frames(packet, 2)
                )

    def test_packet_get_bandwidth(self):
        """Tests `pylibopus.api.decoder.opus_packet_get_bandwidth()`"""

        for ixc in range(0, 256):
            packet = bytes([ixc])
            bwx = ixc >> 4

            # Very cozy code from the test_opus_api.c
            _bwx = pylibopus.BANDWIDTH_NARROWBAND + (((((bwx & 7) * 9) & (63 - (bwx & 8))) + 2 + 12 * ((bwx & 8) != 0)) >> 4)  # NOQA pylint: disable=line-too-long

            self.assertEqual(
                _bwx, pylibopus.api.decoder.packet_get_bandwidth(packet)
            )

    def test_decode(self):
        """opus_decode()"""

        packet = bytes([255, 49])
        for _ in range(2, 51):
            packet += bytes([0])

        dec = pylibopus.api.decoder.create_state(48000, 2)
        try:
            pylibopus.api.decoder.decode(dec, packet, 51, 960, 0)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.INVALID_PACKET)

        packet = bytes([252, 0, 0])
        try:
            pylibopus.api.decoder.decode(dec, packet, -1, 960, 0)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BAD_ARG)

        try:
            pylibopus.api.decoder.decode(dec, packet, 3, 60, 0)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BUFFER_TOO_SMALL)

        try:
            pylibopus.api.decoder.decode(dec, packet, 3, 480, 0)
        except pylibopus.OpusError as exc:
            self.assertEqual(exc.code, pylibopus.BUFFER_TOO_SMALL)

        try:
            pylibopus.api.decoder.decode(dec, packet, 3, 960, 0)
        except pylibopus.OpusError:
            self.fail('Decode failed')

        pylibopus.api.decoder.destroy(dec)

    def test_decode_float(self):
        dec = pylibopus.api.decoder.create_state(48000, 2)

        packet = bytes([252, 0, 0])

        try:
            pylibopus.api.decoder.decode_float(dec, packet, 3, 960, 0)
        except pylibopus.OpusError:
            self.fail('Decode failed')

        pylibopus.api.decoder.destroy(dec)
