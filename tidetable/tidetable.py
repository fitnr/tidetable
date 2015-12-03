#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import re
from csv import DictWriter
from datetime import datetime
import requests
import warnings

BASE_URL = "http://tidesandcurrents.noaa.gov/noaatidepredictions/NOAATidesFacade.jsp"

# All the possible arguments:
#
# http://tidesandcurrents.noaa.gov/noaatidepredictions/NOAATidesFacade.jsp?datatype=Annual+TXT
# Stationid=8517921
# bdate=20151203
# edate=20151204
# timelength=daily
# timeZone=2
# dataUnits=1
# interval=
# StationName=GOWANUS+BAY
# Stationid_=8517921
# state=NY
# primary=Subordinate
# datum=MLLW
# timeUnits=2
# ReferenceStationName=The+Battery
# ReferenceStation=8518750
# HeightOffsetLow=*0.95
# HeightOffsetHigh=*+1.03
# TimeOffsetLow=-12
# TimeOffsetHigh=-18
# pageview=dayly

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
    :time_zone int Time zone for reporting results. Use one of tidetable.GMT, tidetable.LOCAL_STANDARD_TIME, tidetable.LOCAL_TIME. GMT returns results in Greenwich Mean time, LOCAL_STANDARD_TIME returns time in the local standard time zone (ignoring daylight savings), and LOCAL_TIME returns times in a mix of daylight and standard times.
    """

    def __init__(self, stationid, year=None, time_zone=None):
        params = {
            "datatype": "Annual TXT",
            "timeUnits": 1
        }

        self.stationid = params['Stationid'] = stationid

        if time_zone is not None:
            params['timeZone'] = time_zone

        referer = {
            'Referer': '{}?Stationid={}'.format(BASE_URL, stationid)
        }

        if year:
            params['bdate'] = '{:4}0101'.format(year)

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

                setattr(self, key.replace(' ', '_').lower(), value.strip())

            elif line.strip() == '':
                break

        items = parse(lines)

        super(TideTable, self).__init__(items)

        r.close()

    def __repr__(self):
        return 'TideTable(stationid={})'.format(self.stationid)

    def write_csv(self, filename):
        fields = ['datetime', 'pred_ft', 'pred_cm', 'high_low']

        try:
            if hasattr(filename, 'write'):
                f = filename
            else:
                f = open(filename, 'w')

            writer = DictWriter(f, fields)
            writer.writeheader()
            writer.writerows(self)

        finally:
            if f != filename:
                f.close()
