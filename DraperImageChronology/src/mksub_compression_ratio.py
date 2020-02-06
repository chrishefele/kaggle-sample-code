
from os.path import getsize
from scipy.stats import rankdata

DOWNLOAD_DIR = '../download'
SUBMISSION = 'submission.csv'
FLIP_RANKS = False

def flip(days):
    day_fileids = [(day, fileid) for fileid, day in enumerate(days, start=1)]
    return [fileid for day, fileid in sorted(day_fileids)] 

f_in  = open(DOWNLOAD_DIR + '/sample_submission.csv')
f_out = open(SUBMISSION, 'w')

header = f_in.readline()
f_out.write(header)

for line in f_in:

    set_id = int(line.split(',')[0])
    compression_ratios = []
	
    for file_id in (1,2,3,4,5):
	
        basename = 'set%d_%d' % (set_id, file_id)
        f_jpeg = DOWNLOAD_DIR + '/test_sm/' + basename + '.jpeg'
        f_tif  = DOWNLOAD_DIR + '/test/'    + basename + '.tif'

        # compression_ratio = float(getsize(f_jpeg)) / float(getsize(f_tif))
        # compression_ratio = getsize(f_jpeg)
        compression_ratio = getsize(f_tif)
        compression_ratios.append(compression_ratio)
        
    ranks = rankdata(compression_ratios, method='ordinal')
    if FLIP_RANKS:
        ranks = flip(ranks) 
    pred_days = ' '.join(str(int(rank)) for rank in ranks)
    line_out = '%d,%s' % (set_id, pred_days)
    f_out.write(line_out + '\n')
    print set_id, compression_ratios, pred_days

print 'Wrote submission to:', SUBMISSION

