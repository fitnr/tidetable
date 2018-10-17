#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import unittest
from sys import version_info
from datetime import datetime
import csv
import tidetable

if version_info.major > 2:
    from io import StringIO as IO
else:
    from io import BytesIO as IO

class test(unittest.TestCase):

    def setUp(self):
        self.year = datetime.now().year

    def testDownloadTable(self):
        t = tidetable.get(8517921, datum='MLLW')
        self.assertIsInstance(t, tidetable.TideTable)
        self.assertIsInstance(t, list)

        try:
            self.assertIsInstance(t.disclaimer, unicode)
        except NameError:
            self.assertIsInstance(t.disclaimer, str)

        io = IO()
        t.write_csv(io)
        io.seek(0)
        reader = csv.DictReader(io)
        row = next(reader)
        for key in 'pred_ft', 'pred_cm', 'high_low':
            self.assertEqual(row[key], str(t[0][key]))

        del io

    def testBeginDate(self):
        t = tidetable.get(8517921, year=self.year, datum='MLLW')

        try:
            self.assertEqual(t[0]['datetime'].year, self.year)
            self.assertEqual(t[0]['datetime'].month, 1)
            self.assertEqual(t[0]['datetime'].day, 1)
        except AssertionError:
            print(t.raw[0:1000])
            raise

    def testTimeZone(self):
        t = tidetable.get(8517921, datum='MLLW', time_zone=tidetable.GMT)
        self.assertEqual(t.time_zone, 'GMT')

        s = tidetable.get(8517921, datum='MLLW', time_zone=tidetable.LOCAL_STANDARD_TIME)
        self.assertEqual(s.time_zone, 'LST')

        self.assertNotEqual(t[0]['datetime'], s[0]['datetime'])

if __name__ == '__main__':
    unittest.main()
