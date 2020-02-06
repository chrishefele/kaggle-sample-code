
from find_orig_fileid import find_orig_fileid

from os.path import getsize
from scipy.stats import rankdata

DOWNLOAD_DIR = '../download'
SUBMISSION = 'sub_orig_fileid.csv'
FLIP_RANKS = False

def flip(days):
    day_fileids = [(day, fileid) for fileid, day in enumerate(days, start=1)]
    return [fileid for day, fileid in sorted(day_fileids)] 

f_in  = open(DOWNLOAD_DIR + '/sample_submission.csv')
f_out = open(SUBMISSION, 'w')

header = f_in.readline()
f_out.write(header)
print header

for line in f_in:

    set_id = int(line.split(',')[0])
    orig_fileid = find_orig_fileid(set_id)

    ranks = 5 * [2]
    ranks[orig_fileid - 1] = 1
    pred_days = ' '.join(str(int(rank)) for rank in ranks)
    line_out = '%d,%s' % (set_id, pred_days)
    f_out.write(line_out + '\n')

    print line_out

print 'Wrote submission to:', SUBMISSION

