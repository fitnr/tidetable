#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

from setuptools import setup

try:
    readme = open('README.rst').read()
except:
    readme = open('README.md').read()

setup(
    name='tidetable',
    version='0.1.2',
    description='Thin API for NOAA tide tables',
    long_description=readme,
    keywords='noaa',
    author='Neil Freeman',
    author_email='contact@fakeisthenewreal.org',
    url='https://github.com/fitnr/tidetable',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=['tidetable'],
    include_package_data=False,
    install_requires=[
        'requests'
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            # 'tidetable=tidetable.cli:main',
        ],
    },
)
