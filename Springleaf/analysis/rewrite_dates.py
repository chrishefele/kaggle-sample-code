import sys
from datetime import datetime


def datetimeElapsed(datetimeStr, datetimeOrigin="01JAN00:00:00:00"):
    if not datetimeStr:
        return -1
    fmt = "%d%b%y:%H:%M:%S"
    elapsed =   datetime.strptime(datetimeStr,    fmt) - \
                datetime.strptime(datetimeOrigin, fmt)
    assert elapsed.days >= 0 
    return elapsed.days

fin = open(sys.argv[1], 'r')
fin.readline().strip()
for line in fin:
    fields   = line.split(',')
    ID_      = int(fields[0])
    date_int = datetimeElapsed(fields[1])
    target   = int(fields[2])
    print ID_,",", date_int,",",target


