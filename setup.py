#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 N.T.WORKS Authors. All Rights Reserved.
#
#      http://opensource.org/licenses/mit-license.php
#

from distutils.core import setup

_AUTHOR     = 'N.T.WORKS'
_EMAIL      = 'nagisc007@yahoo.co.jp'
_VERSION    = '1.0.0'

setup(
    name='pegparser',
    version=_VERSION,
    author=_AUTHOR,
    author_email=_EMAIL,
    packages=['pegparser', 'pegparser.test'],
    url='https://github.com/nagisc007/pegparser',
    license='LICENSE.txt',
    description='A simple implementation using PEG parser in Python',
    long_description=open('README.md').read(),
    requires=['',],
    provides=['pegparser (' + _version + ')',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Japanese',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
