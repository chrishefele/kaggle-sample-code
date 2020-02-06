import whaleIO

sig_response = whaleIO.read_signal_response()

for line in open('../data/dups/train.dups'):
    tokens = line.split('/')
    if len(tokens) >= 2:
        sig_fname = tokens[1].strip()
        print sig_fname, sig_response[sig_fname]
    else:
        print

