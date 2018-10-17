import sys
import argparse
from . import tidetable


def main():
    parser = argparse.ArgumentParser('tidetable')
    parser.add_argument('stationid', metavar='station-id', type=str, help='NOAA station id')
    parser.add_argument('--year', type=int, help='year')
    parser.add_argument('--datum', choices=tidetable.DATUMS, help='output datum')
    args = parser.parse_args()

    tidetable.TideTable(args.stationid, year=args.year, datum=args.datum).write_csv(sys.stdout)


if __name__ == '__main__':
    main()
