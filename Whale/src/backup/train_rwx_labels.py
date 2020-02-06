import whaleIO
import sys

sig_response = whaleIO.read_signal_response()

for line in open(sys.argv[1]):
    sig_fname = line.strip()
    if sig_fname:
        print sig_fname,',',sig_response[sig_fname]
