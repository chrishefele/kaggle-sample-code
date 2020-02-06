

import csv
import sys
import time
from dateutil.parser import parse as dateparse

CSV_TRAIN = "../download/train_ver2.csv"

# print dateparse("2012-01-27")

fin = open(CSV_TRAIN)
reader = csv.reader(fin)
header = reader.next()
print "HEADER:", header
for n, row in enumerate(reader):
    print n, row


