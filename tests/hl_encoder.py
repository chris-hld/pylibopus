#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
#

"""Tests for a high-level Decoder object"""

import unittest

import pylibopus

__author__ = 'Никита Кузнецов <self@svartalf.info>'
__copyright__ = 'Copyright (c) 2012, SvartalF'
__license__ = 'BSD 3-Clause License'


class EncoderTest(unittest.TestCase):

    def test_create(self):
        try:
            pylibopus.Encoder(1000, 3, pylibopus.APPLICATION_AUDIO)
        except pylibopus.OpusError as ex:
            self.assertEqual(ex.code, pylibopus.BAD_ARG)

        pylibopus.Encoder(48000, 2, pylibopus.APPLICATION_AUDIO)

    @classmethod
    def test_reset_state(cls):
        encoder = pylibopus.Encoder(48000, 2, pylibopus.APPLICATION_AUDIO)
        encoder.reset_state()
