tidetable
=========

Tidetable is a Python module for downloading annual tide prediction tables from the [NOAA Tides & Currents](http://tidesandcurrents.noaa.gov) site.

Install with `pip install tidetable`.

## Basics

First, [identify your tide station](http://tidesandcurrents.noaa.gov/tide_predictions.html) and it's Station ID number.

Then, use the `get` method to download the table. This returns a `TideTable` object, which is just a `list` with a few additional metadata parameters. 

````python
>>> import tidetable
>>> table = tidetable.get(8416092)
>>> table
TideTable(stationid=8416092)
>>> table[0]
{'pred_cm': 149.0, 'datetime': datetime.datetime(2014, 12, 31, 3, 44), 'pred_ft': 4.9, 'high_low': 'H'}
>>> t.stationid, t.stationname
('8416092', 'Monhegan Island')
>>> table.datum
'MLLW'
````

### Time frames

By default, the NOAA returns the tide prediction table for the current year. To get years in the recent past or future, use the `year` keyword argument. It seems that roughly five years in the past and two years in the future are available. There isn't a way to get smaller time ranges of predictions than a full year.

````python
>>> import tidetable
>>> table = tidetable.get(8416092, year=2016)
>>> table[4]['datetime']
datetime.datetime(2016, 1, 1, 3, 39)
````

(Note that the first few rows returned may be for the previous year.)

### Writing

The `TideTable` object has a write_csv method. It accepts either a file name or any file-like object.

````python
import tidetable
table = tidetable.get(8416092)
table.write_csv('tide_table.csv')
````

### Time zones

As you can see, `TideTable` is a list of `dict`s, each of which has a `datetime`, a prediction in feet and cm, and a high-or-low flag. The predictions are relative to the `datum`, which in this case is MLLW, or the mean lower low water level. Note that MLLW is different from sea level.

By default, the `datetime` is in the local time, which could be standard or daylight savings time. Use the `time_zone` keyword argument to fetch times in either GMT or the local standard time zone. TideTable always returns naive `datetime` objects.

Use these constants for specifying the time zone: `tidetable.GMT`, `tidetable.LOCAL_STANDARD_TIME`, `tidetable.LOCAL_TIME`.

````python
>>> import tidetable
>>> table = tidetable.get(8416092, time_zone=tidetable.GMT)
>>> table[0]['datetime']
datetime.datetime(2014, 12, 31, 0, 15)
````

(Note the difference from the datetime in the first example, which is in Eastern Standard Time)

