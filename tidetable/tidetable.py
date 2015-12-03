#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import re
from datetime import datetime
import requests

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
# print_download=true
# Threshold=
# thresholdvalue=


GMT = 0 
LOCAL_STANDARD_TIME = 1
LOCAL_TIME = 2

def get(stationid, **kwargs):
    return TideTable(stationid, **kwargs)

class TideTable(list):
    """
    Downloads an NOAA tide table, returning a list of predictions.
    Object also includes some metadata about the predictions.

    :stationid str Tide observation station
    :begin datetime date to begin predictions. Default is previous December 31
    :timezone int Time zone for reporting results. Use one of tidetable.GMT, tidetable.LOCAL_STANDARD_TIME, tidetable.LOCAL_TIME. GMT returns results in Greenwich Mean time, LOCAL_STANDARD_TIME returns time in the local standard time zone (ignoring daylight savings), and LOCAL_TIME returns times in a mix of daylight and standard times.
    """

    def __init__(self, stationid, begin=None, end=None, timezone=None):
        params = {
            "datatype": "Annual TXT",
            "timeUnits": 1,
            'timeZone': timezone or LOCAL_TIME
        }

        self.stationid = params['Stationid'] = stationid

        if end and begin and end < begin:
            end, begin = begin, end

        if begin:
            params['bdate'] = begin.strftime('%Y%m%d')
            params['edate'] = '{}{}'.format(begin.year + 1, begin.strftime('%m%d'))

        if end:
            params['edate'] = end.strftime('%Y%m%d')

        referer = {
            'Referer': '{}?Stationid={}'.format(BASE_URL, stationid)
        }

        self.r = r = requests.get(BASE_URL, params=params, headers=referer)
        lines = r.iter_lines()

        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                setattr(self, key.replace(' ', '_').lower(), value.strip())

            elif line.strip() == '':
                break

        items = self._parse(lines)

        super(TideTable, self).__init__(items)

    def _parse(self, lines):
        tab = re.compile(r'\t+')
        hed = next(lines)

        header = [x.strip() for x in re.split(tab, hed)]
        results = list()

        for row in lines:
            result = {}
            prelim = dict(zip(header, re.split(tab, row)))

            try:
                dt = prelim['Date'] + ' ' + prelim['Time']

                result['datetime'] = datetime.strptime(dt, '%Y/%m/%d %H:%M')

                result['pred_ft'] = float(prelim['Pred(Ft)'])
                result['pred_cm'] = float(prelim['Pred(cm)'])
                result['high_low'] = prelim['High/Low']

            except KeyError as e:
                pass

            results.append(result)

        return results

    def __repr__(self):
        return 'TideTable(stationid={})'.format(self.stationid)
