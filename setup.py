#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python libopus Package."""

import setuptools  # type: ignore

setuptools.setup(
    name='pylibopus',
    version='3.0.5',
    author='Никита Кузнецов',
    author_email='self@svartalf.info',
    maintainer='Chris Hold',
    maintainer_email='info@chrisholdaudio.com',
    license='BSD 3-Clause License',
    url='https://github.com/chris-hld/pylibopus',
    description='Python bindings to the libopus, IETF low-delay audio codec',
    packages=('pylibopus', 'pylibopus.api'),
    test_suite='tests',
    zip_safe=False,
    tests_require=[
        'coverage >= 4.4.1',
        'nose >= 1.3.7',
    ],
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ),
)
