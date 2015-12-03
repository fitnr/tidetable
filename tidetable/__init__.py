#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

__version__ = '0.1.0'

__all__ = ['tidetable']

GMT = 0
LOCAL_STANDARD_TIME = 1
LOCAL_TIME = 2

from .tidetable import get, TideTable
