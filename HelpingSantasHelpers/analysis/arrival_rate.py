import datetime
import csv
from collections import defaultdict
from numpy import array
import numpy

TOY_FILE = '../download/toys_rev2.csv'

def convert_to_minute(arrival):
    """ Converts the arrival time string to minutes since the reference start time,
    Jan 1, 2014 at 00:00 (aka, midnight Dec 31, 2013)
    :param arrival: string in format '2014 12 17 7 03' for Dec 17, 2014 at 7:03 am
    :return: integer (minutes since arrival time)
    """
    time = arrival.split(' ')
    dd = datetime.datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]))
    age = dd - datetime.datetime(2014, 1, 1, 0, 0)
    return int(age.total_seconds() / 60)


def read_toys(toy_file):

    arrival_count = defaultdict(int)
    arrival_work  = defaultdict(int)
    arrival_works = defaultdict(list)

    with open(toy_file, 'rb') as f:
        fcsv = csv.reader(f)
        fcsv.next()  # header row
        for row in fcsv:
            work = int(row[2])
            year, month, day, hour, minute = row[1].split()
            t = convert_to_minute(' '.join([year, month, day, "0 0"]))
            arrival_count[t] += 1
            arrival_work[ t] += work 
            arrival_works[t].append(work)

    arrival_median = { t:numpy.median(array(arrival_works[t])) for t in arrival_works } 
    return arrival_count, arrival_work, arrival_median

def main():

    arrival_count, arrival_work, arrival_median = read_toys(TOY_FILE)
    print "minute,arrival_count,arrival_minutes,arrival_median"
    for t in sorted(arrival_count):
        print t,",", arrival_count[t], ",", arrival_work[t], ",", arrival_median[t]


main()

