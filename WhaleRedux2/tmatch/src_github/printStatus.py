import sys

PRINT_MOD = 100

def printStatus(i):
    if i % PRINT_MOD == 0:
        print i,
        sys.stdout.flush()

