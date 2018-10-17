#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>
import os
import re
import errno
from csv import DictWriter
from datetime import datetime
import warnings
from signal import signal, SIGPIPE, SIG_DFL
import requests

signal(SIGPIPE, SIG_DFL)

GMT = 'GMT'
LOCAL_STANDARD_TIME = 'LST'
DATUMS = "STND", "MHHW", "MHW", "MTL", "MSL", "MLW", "MLLW"
BASE_URL = "https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi"


def get(stationid, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return TideTable(stationid, **kwargs)


def parse(lines):
    tab = re.compile(r'\t+')

    hed = next(lines).decode('ascii')
    header = [x.strip() for x in re.split(tab, hed)]
    results = list()

    for row in lines:
        result = {}
        prelim = dict(zip(header, re.split(tab, row.decode('ascii'))))

        try:
            dt = prelim['Date'] + ' ' + prelim['Time']
            result['datetime'] = datetime.strptime(dt, '%Y/%m/%d %H:%M')

            result['pred_ft'] = float(prelim['Pred(Ft)'])
            result['pred_cm'] = float(prelim['Pred(cm)'])
            result['high_low'] = prelim['High/Low']

        except KeyError as e:
            continue

        if len(result) > 0:
            results.append(result)

    return results


class TideTable(list):

    """
    Downloads an NOAA tide table, returning a list of predictions.
    Object also includes some metadata about the predictions.

    :stationid str Tide observation station
    :year int year to fetch predictions for. Default is current year
    :time_zone int Time zone for reporting results.
        Use one of tidetable.GMT, tidetable.LOCAL_STANDARD_TIME, tidetable.LOCAL_TIME. GMT returns
        results in Greenwich Mean time, LOCAL_STANDARD_TIME returns time in the local standard
        time zone (ignoring daylight savings), and LOCAL_TIME returns times in a mix of daylight
        and standard times.
    :datum str A vertical datum. Not all tide stations report in all datums, empty results may
        reflect an unspoorted datum.
    """

    def __init__(self, stationid, year=None, time_zone=None, datum=None):
        # https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi
        # stnid=1611400&threshold=&thresholdDirection=greaterThan&bdate=2018
        # timezone=GMT
        # datum=STND
        # clock=24hour
        # type=txt
        # annual=true
        self.datum = (datum or DATUMS[0]).upper()
        if self.datum not in DATUMS:
            self.datum = DATUMS[0]

        self._tz = time_zone or GMT
        self._stationid = stationid
        self._year = year or datetime.now().year

        params = {
            "type": "txt",
            "clock": "24hour",
            "annual": "true",
            "datum": self.datum,
            "timezone": self._tz,
            "stnid": self.stationid,
            "bdate": self.year
        }

        referer = {'Referer': BASE_URL}

        r = requests.get(BASE_URL, params=params, headers=referer)
        lines = r.iter_lines()

        setattr(self, 'url', r.url)
        setattr(self, 'raw', r.text)

        for line in lines:
            line = line.decode('ascii')

            if ': ' in line:
                key, value = line.split(': ', 1)

                # reserved name
                if key.lower() == 'from':
                    key = 'period'

                try:
                    setattr(self, key.replace(' ', '_').lower(), value.strip())
                except AttributeError:
                    pass

            elif line.strip() == '':
                break

        try:
            items = parse(lines)
        except StopIteration:
            # We didn't get any results. Fail gracefully.
            items = []

        super(TideTable, self).__init__(items)
        r.close()

    def __repr__(self):
        year = ', year={}'.format(self.year) if hasattr(self, 'year') else ''
        tz = ', time_zone={}'.format(self._tz) if hasattr(self, '_tz') else ''

        return 'tidetable.TideTable(stationid={}{year}{tz})'.format(self.stationid, year=year, tz=tz)

    @property
    def stationid(self):
        return self._stationid

    @property
    def year(self):
        return self._year

    @property
    def time_zone(self):
        return self._tz

    def write_csv(self, filename):
        fields = ['datetime', 'pred_ft', 'pred_cm', 'high_low']

        try:
            if hasattr(filename, 'write'):
                f = filename
            else:
                f = open(filename, 'w')

            writer = DictWriter(f, fields, lineterminator=os.linesep)
            try:
                writer.writeheader()
                writer.writerows(self)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass

            except BrokenPipeError as e:
                pass

        finally:
            if f != filename:
                f.close()
