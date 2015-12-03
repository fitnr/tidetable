#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import unittest
import tidetable
from datetime import datetime
from sys import version_info

if version_info.major > 2:
    from io import StringIO as IO
else:
    from io import BytesIO as IO

class test(unittest.TestCase):
    def testDownloadTable(self):
        t = tidetable.get(8517921)
        assert isinstance(t, tidetable.TideTable)
        assert isinstance(t, list)

        try:
            assert isinstance(t.disclaimer, unicode)
        except NameError:
            assert isinstance(t.disclaimer, str)

        io = IO()
        t.write_csv(io)

    def testBeginDate(self):
        t = tidetable.get(8517921, year=2016)

        try:
            assert t[0]['datetime'].year == 2015
            assert t[0]['datetime'].month == 12
            assert t[0]['datetime'].day == 31
        except:
            print (t.raw)

    def testTimeZone(self):
        t = tidetable.get(8517921, time_zone=tidetable.GMT)
        assert t.time_zone == 'GMT'

        s = tidetable.get(8517921, time_zone=tidetable.LOCAL_STANDARD_TIME)
        assert s.time_zone == 'LST'

        assert t[0]['datetime'] != s[0]['datetime']

if __name__ == '__main__':
    unittest.main()
